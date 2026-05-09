# src/main.py
"""Punto de entrada del extractor"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import PipelineConfig
from src.infrastructure.adapters.github_adapter import GitHubAdapter
from src.infrastructure.adapters.database_adapter import DatabaseAdapter
from src.infrastructure.adapters.drive_adapter import DriveAdapter
from src.application.use_cases.extract_github_data import ExtractGitHubDataUseCase
from src.application.use_cases.generate_report import GenerateReportUseCase

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config_from_drive(drive_adapter: DriveAdapter) -> dict:
    """Carga configuración desde Drive"""
    try:
        config = drive_adapter.download_config("config.json")
        logger.info("Configuration loaded from Drive")
        return config
    except FileNotFoundError:
        logger.warning("Config file not in Drive, using default")
        return {
            "repositories": [
                {"owner": "pandas-dev", "name": "pandas"},
                {"owner": "microsoft", "name": "vscode"}
            ],
            "last_extraction": None
        }


def main():
    """Función principal"""
    
    # Cargar configuración
    config = PipelineConfig()
    
    # Inicializar adaptadores
    github = GitHubAdapter(config.github.token)
    db = DatabaseAdapter(
        host=config.database.host,
        user=config.database.user,
        password=config.database.password,
        database=config.database.database
    )
    drive = DriveAdapter(
        credentials_path=config.google_drive.credentials_path,
        folder_id=config.google_drive.folder_id
    )
    
    try:
        # Cargar repositorios desde Drive
        drive_config = load_config_from_drive(drive)
        repositories = drive_config.get("repositories", [])
        
        # Determinar tipo de extracción
        extraction_type = sys.argv[1] if len(sys.argv) > 1 else "full"
        since = drive_config.get("last_extraction") if extraction_type == "incremental" else None
        
        logger.info(f"Running {extraction_type} extraction")
        
        # Ejecutar extracción
        extract_use_case = ExtractGitHubDataUseCase(github, db)
        extraction_result = extract_use_case.execute(repositories, since)
        
        logger.info(f"Extraction result: {extraction_result}")
        
        # Generar reporte
        report_use_case = GenerateReportUseCase(db, drive)
        report_result = report_use_case.execute()
        
        logger.info(f"Report result: {report_result}")
        
        # Actualizar last_extraction
        new_timestamp = datetime.now().isoformat()
        logger.info(f"Next extraction will use: {new_timestamp}")
        
        return 0
        
    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        return 1
        
    finally:
        github.close()
        db.close()


if __name__ == "__main__":
    sys.exit(main())
