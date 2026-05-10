import sys
import os
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import PipelineConfig
from src.infrastructure.database import Database
from src.infrastructure.adapters.github_adapter import GitHubAdapter
from src.infrastructure.adapters.database_adapter import DatabaseAdapter
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
        # Cargar repositorios desde archivo local
        pipeline_config = load_config_from_file("config.json")
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
