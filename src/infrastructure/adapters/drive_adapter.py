import json
import logging
from pathlib import Path
from typing import Dict
from io import BytesIO

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from src.domain.ports.drive_client import DriveClientPort

logger = logging.getLogger(__name__)


class DriveAdapter(DriveClientPort):
    """Implementación del adaptador de Google Drive"""
    
    def __init__(self, credentials_path: Path, folder_id: str):
        self.credentials_path = credentials_path
        self.folder_id = folder_id
        
        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=[
                'https://www.googleapis.com/auth/drive.readonly',
                'https://www.googleapis.com/auth/drive.file'
            ]
        )
        self.service = build('drive', 'v3', credentials=credentials)
        logger.info(f"Drive adapter initialized. Folder: {folder_id}")
    
    def download_config(self, filename: str="config.json") -> Dict:
        """Descarga archivo de configuración desde Drive"""
        try:
            # Buscar archivo
            results = self.service.files().list(
                q=f"name = '{filename}' and '{self.folder_id}' in parents",
                fields="files(id, name)"
            ).execute()
            
            files = results.get("files", [])
            
            if not files:
                raise FileNotFoundError(f"File '{filename}' not found in Drive")
            
            file_id = files[0]["id"]
            
            # Descargar contenido
            request = self.service.files().get_media(fileId=file_id)
            content = request.execute()
            
            config = json.loads(content.decode('utf-8'))
            logger.info(f"Config loaded from Drive: {filename}")
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to download config: {e}")
            raise
    
    def upload_file(self, local_path: str, filename: str, folder_id: str=None):
        """Sube archivo a Drive"""
        target_folder = folder_id or self.folder_id
        
        # Buscar si ya existe
        results = self.service.files().list(
            q=f"name = '{filename}' and '{target_folder}' in parents",
            fields="files(id)"
        ).execute()
        
        existing = results.get("files", [])
        
        # Leer archivo
        with open(local_path, 'rb') as f:
            file_content = f.read()
        
        media = MediaIoBaseUpload(
            BytesIO(file_content),
            mimetype='text/csv'
        )
        
        if existing:
            # Actualizar
            file_id = existing[0]['id']
            self.service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            logger.info(f"File updated: {filename}")
        else:
            # Crear nuevo
            file_metadata = {
                'name': filename,
                'parents': [target_folder]
            }
            self.service.files().create(
                body=file_metadata,
                media_body=media
            ).execute()
            logger.info(f"File created: {filename}")
