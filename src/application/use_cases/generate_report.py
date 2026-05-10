import logging
import pandas as pd
from typing import Dict

from src.domain.ports.database import DatabasePort
from src.domain.ports.drive_client import DriveClientPort

logger = logging.getLogger(__name__)


class GenerateReportUseCase:
    """Caso de uso para generar reporte CSV"""
    
    def __init__(self, database: DatabasePort, drive_client: DriveClientPort):
        self.db = database
        self.drive = drive_client
    
    def execute(self, local_path: str="/tmp/reporte_github.csv") -> Dict:
        """Genera reporte y lo sube a Drive"""
        
        # 1. Obtener datos resumidos
        summary = self.db.get_summary()
        
        if not summary:
            logger.warning("No data to report")
            return {"status": "no_data"}
        
        # 2. Crear DataFrame y guardar CSV
        df = pd.DataFrame(summary)
        df.to_csv(local_path, index=False)
        logger.info(f"CSV generated: {local_path}")
        
        # 3. Subir a Drive
        filename = "reporte_github.csv"
        self.drive.upload_file(local_path, filename)
        
        return {
            "status": "success",
            "filename": filename,
            "records": len(df),
            "summary": summary
        }
