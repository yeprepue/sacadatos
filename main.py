import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import PipelineConfig
from src.infrastructure.database import Database
from src.infrastructure.adapters.github_adapter import GitHubAdapter
from src.infrastructure.adapters.database_adapter import DatabaseAdapter
from src.infrastructure.adapters.drive_adapter import DriveAdapter
from src.application.use_cases.extract_github_data import ExtractGitHubDataUseCase
from src.application.use_cases.generate_report import GenerateReportUseCase
from src.config.logging_config import logger


def load_config_from_drive(drive_adapter):
    config = drive_adapter.download_config("config.json")
    logger.info("Configuración cargada desde Drive")
    return config


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
        
        logger.info(f"Tipo de extracción: {extraction_type}")
        
        # Ejecutar extracción
        extract_use_case = ExtractGitHubDataUseCase(github, db_adapter)
        extraction_result = extract_use_case.execute(repositories, since)
        
        logger.info(f"Resultado extracción: {extraction_result}")
        
        # Generar reporte
        report_use_case = GenerateReportUseCase(db_adapter, drive)
        report_result = report_use_case.execute()
        
        logger.info(f"Resultado reporte: {report_result}")
        
        logger.success("Pipeline completado exitosamente!")
        return 0
        
    except Exception as e:
        logger.exception(f"Pipeline falló: {e}")
        return 1
        
    finally:
        github.close()
        db_adapter.close()


if __name__ == "__main__":
    sys.exit(main())
