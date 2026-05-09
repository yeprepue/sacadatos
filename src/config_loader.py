from google.oauth2 import service_account
from googleapiclient.discovery import build
import json


class ConfigLoader:

    def __init__(self, credentials_path: str, folder_id: str):
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        self.service = build('drive', 'v3', credentials=self.credentials)
        self.folder_id = folder_id

    def get_config(self, filename: str='repos_config.json') -> dict:
        # Buscar archivo en Drive
        results = self.service.files().list(
            q=f"name='{filename}' and '{self.folder_id}' in parents",
            fields="files(id, name)"
        ).execute()
        
        file_id = results['files'][0]['id']
        
        # Descargar contenido
        request = self.service.files().get_media(fileId=file_id)
        content = request.execute()
        
        return json.loads(content)

    def update_last_extraction(self, timestamp: str):
        """Actualiza la fecha de última extracción"""
        config = self.get_config()
        config['last_extraction'] = timestamp
        # Aquí subirías la actualización a Drive
        return config
