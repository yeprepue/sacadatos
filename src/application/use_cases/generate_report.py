import re
import psycopg2
import pandas as pd
import os
from typing import Dict
from datetime import datetime
from pathlib import Path

from src.config.logging_config import logger


def clean_string(value):
    """Remove control characters not allowed in CSV"""
    if isinstance(value, str):
        value = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', value)
        value = value.replace('\x00', '')
    return value


def generate_csv_report(output_path: str=None):
    """
    Genera reporte CSV con timestamp en la carpeta reports/
    
    Args:
        output_path: Ruta específica (opcional). Si no se provee, 
                    crea automáticamente con fecha/hora en reports/
    
    Returns:
        Dict con estado, ruta del archivo y cantidad de filas
    """
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DB")
    )
    # Crear carpeta reports si no existe
    reports_dir = Path(__file__).parent.parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Generar nombre con timestamp si no se especificó ruta
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reporte_{timestamp}.csv"
        output_path = str(reports_dir / filename)
    else:
        # Si se especificó ruta, asegurar que la carpeta existe
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    try:
        repos_df = pd.read_sql("SELECT id, owner||'/'||name as repo FROM repositories", conn)
        
        rows = []
        for _, repo in repos_df.iterrows():
            repo_id = repo['id']
            repo_name = repo['repo']
            
            issues_df = pd.read_sql("""
                SELECT id, number, title, state, created_at, updated_at, closed_at, user_login
                FROM issues WHERE repo_id = %s
            """, conn, params=[repo_id])
            
            for _, issue in issues_df.iterrows():
                rows.append({
                    'repo': repo_name,
                    'type': 'issue',
                    'id': issue['id'],
                    'number': issue['number'],
                    'title': clean_string(issue['title']),
                    'state': issue['state'],
                    'created_at': issue['created_at'],
                    'updated_at': issue['updated_at'],
                    'closed_at': issue['closed_at'],
                    'author': clean_string(issue['user_login']) if issue['user_login'] else None
                })
            
            commits_df = pd.read_sql("""
                SELECT sha, message, author_login, author_date
                FROM commits WHERE repo_id = %s
            """, conn, params=[repo_id])
            
            for _, commit in commits_df.iterrows():
                rows.append({
                    'repo': repo_name,
                    'type': 'commit',
                    'sha': commit['sha'],
                    'message': clean_string(commit['message']) if commit['message'] else None,
                    'author': clean_string(commit['author_login']) if commit['author_login'] else None,
                    'date': commit['author_date']
                })
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"CSV generado: {output_path} ({len(rows)} filas)")
        
        return {"status": "success", "file": output_path, "rows": len(rows)}
        
    except Exception as e:
        logger.error(f"Error generando reporte: {str(e)}")
        return {"status": "error", "message": str(e)}
        
    finally:
        conn.close()


class GenerateReportUseCase:

    def __init__(self, database=None, drive_client=None):
        self.db = database
        self.drive = drive_client

    def execute(self, local_path: str=None) -> Dict:
        """
        Ejecuta la generación del reporte
        
        Args:
            local_path: Ruta específica (opcional). Si es None, 
                crea automáticamente en reports/ con timestamp
        """
        return generate_csv_report(local_path)


if __name__ == "__main__":
    # Prueba directa
    result = generate_csv_report()
    print(f"Resultado: {result}")
