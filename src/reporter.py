import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io


class Reporter:

    def __init__(self, credentials_path: str, folder_id: str):
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        self.service = build('drive', 'v3', credentials=self.credentials)
        self.folder_id = folder_id

    def generate_summary(self, storage) -> pd.DataFrame:
        """Genera resumen de issues y commits por repositorio"""
        query = """
            SELECT 
                r.owner || '/' || r.name as repository,
                COUNT(DISTINCT i.id) as total_issues,
                COUNT(DISTINCT CASE WHEN i.state = 'open' THEN i.id END) as open_issues,
                COUNT(DISTINCT CASE WHEN i.state = 'closed' THEN i.id END) as closed_issues,
                COUNT(DISTINCT c.sha) as total_commits
            FROM repositories r
            LEFT JOIN issues i ON r.id = i.repo_id
            LEFT JOIN commits c ON r.id = c.repo_id
            GROUP BY r.id, r.owner, r.name
            ORDER BY r.name
        """
        
        with storage.conn.cursor() as cur:
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            data = cur.fetchall()
        
        df = pd.DataFrame(data, columns=columns)
        return df

    def upload_to_drive(self, df: pd.DataFrame, filename: str='reporte_github.csv'):
        """Sube el CSV a Google Drive"""
        # Convertir DataFrame a CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        
        # Crear archivo para Drive
        media = MediaIoBaseUpload(
            io.BytesIO(csv_buffer.getvalue().encode()),
            mimetype='text/csv'
        )
        
        # Buscar si ya existe y eliminar
        existing = self.service.files().list(
            q=f"name='{filename}' and '{self.folder_id}' in parents",
            fields="files(id)"
        ).execute()
        
        if existing.get('files'):
            file_id = existing['files'][0]['id']
            self.service.files().delete(fileId=file_id).execute()
        
        # Subir archivo
        file_metadata = {
            'name': filename,
            'parents': [self.folder_id]
        }
        
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        print(f"Reporte subido: https://drive.google.com/file/d/{file['id']}/view")
        return file
