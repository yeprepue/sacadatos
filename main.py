import sys
import os
import json
import requests
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import PipelineConfig
from src.infrastructure.database import Database
from src.infrastructure.adapters.github_adapter import GitHubAdapter
from src.infrastructure.adapters.database_adapter import DatabaseAdapter
from src.infrastructure.adapters.drive_adapter import DriveAdapter
from src.application.use_cases.extract_github_data import ExtractGitHubDataUseCase
from src.config.logging_config import logger


def load_config_from_file(config_path: str = "config.json") -> dict:
    """Cargar configuración desde archivo local"""
    if Path(config_path).exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
            logger.info(f"Configuración cargada desde {config_path}")
            return config
    else:
        logger.warning(f"Archivo {config_path} no encontrado, usando configuración por defecto")
        return {
            "repositories": [
                {"owner": "pandas-dev", "name": "pandas"},
                {"owner": "microsoft", "name": "vscode"}
            ],
            "last_extraction": None
        }


def load_config_from_public_drive(file_id: str) -> dict:
    """Cargar configuración desde Google Drive público (sin credenciales)"""
    try:
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        content = response.text
        
        # Manejar caso donde Google devuelve HTML con warning de virus
        if content.startswith("<!DOCTYPE") or "download_warning" in content:
            import re
            match = re.search(r'confirm=([a-zA-Z0-9_-]+)', content)
            if match:
                confirm_url = f"https://drive.google.com/uc?export=download&confirm={match.group(1)}&id={file_id}"
                response = requests.get(confirm_url, timeout=30)
                response.raise_for_status()
                content = response.text
        
        config = json.loads(content)
        logger.info(f"Config loaded from public Drive: {file_id}")
        return config
    except Exception as e:
        logger.error(f"Failed to load config from public Drive: {e}")
        return None


def load_config_from_drive(config: PipelineConfig) -> dict:
    """Cargar configuración desde Google Drive"""
    file_id = config.google_drive.config_file_id
    
    if file_id:
        return load_config_from_public_drive(file_id)
    
    try:
        drive = DriveAdapter(
            credentials_path=config.google_drive.credentials_path,
            folder_id=config.google_drive.folder_id
        )
        return drive.download_config("config.json")
    except Exception as e:
        logger.error(f"Failed to load config from Drive: {e}")
        return None


def main():
    logger.info("=" * 50)
    logger.info("Iniciando GitHub Data Pipeline")
    logger.info("=" * 50)
    
    # Cargar configuración
    config = PipelineConfig()
    
    # Inicializar adaptadores
    github = GitHubAdapter(config.github.token)
    db = Database(config.database.connection_string)
    db_adapter = DatabaseAdapter(db)
    
    try:
        # Cargar repositorios desde Google Drive
        logger.info("Cargando configuración desde Google Drive...")
        pipeline_config = load_config_from_drive(config)
        
        if not pipeline_config:
            logger.warning("Fallo al cargar desde Drive, intentando archivo local...")
            pipeline_config = load_config_from_file("config.json")
        
        if not pipeline_config or "repositories" not in pipeline_config:
            logger.warning("Usando configuración por defecto")
            pipeline_config = {
                "repositories": [
                    {"owner": "pandas-dev", "name": "pandas"},
                    {"owner": "microsoft", "name": "vscode"}
                ],
                "last_extraction": None
            }
        
        repositories = pipeline_config.get("repositories", [])
        
        # Determinar tipo de extracción
        extraction_type = sys.argv[1] if len(sys.argv) > 1 else "full"
        since = pipeline_config.get("last_extraction") if extraction_type == "incremental" else None
        
        logger.info(f"Tipo de extracción: {extraction_type}")
        logger.info(f"Repositorios a procesar: {len(repositories)}")
        
        # Ejecutar extracción
        extract_use_case = ExtractGitHubDataUseCase(github, db_adapter)
        extraction_result = extract_use_case.execute(repositories, since)
        
        logger.info(f"Resultado extracción: {extraction_result}")
        logger.info("Pipeline completado exitosamente!")
        return 0
        
    except Exception as e:
        logger.exception(f"Pipeline falló: {e}")
        return 1
        
    finally:
        github.close()
        db_adapter.close()


if __name__ == "__main__":
    sys.exit(main())
