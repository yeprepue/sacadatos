import pandas as pd
from typing import Dict
from src.domain.ports.database import DatabasePort
from src.domain.ports.drive_client import DriveClientPort
from src.config.logging_config import logger

class GenerateReportUseCase:
    def __init__(self, database: DatabasePort, drive_client: DriveClientPort):
        self.db = database
        self.drive = drive_client
    
    def execute(self, local_path: str = "/tmp/reporte_github.csv") -> Dict:
        summary = self.db.get_summary()
        
        if not summary:
            logger.warning("No hay datos para reportar")
            return {"status": "no_data"}
        
        df = pd.DataFrame(summary)
        df.to_csv(local_path, index=False)
        logger.info(f"CSV generado: {local_path}")
        
        filename = "reporte_github.csv"
        self.drive.upload_file(local_path, filename)
        
        return {
            "status": "success",
            "filename": filename,
            "records": len(df),
            "summary": summary
        }
