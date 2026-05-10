import json
from pathlib import Path
from typing import Dict
from io import BytesIO

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from src.domain.ports.drive_client import DriveClientPort
from src.config.logging_config import logger


class DriveAdapter(DriveClientPort):
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
    
    def download_config(self, filename: str = "config.json") -> Dict:
        try:
            results = self.service.files().list(
                q=f"name = '{filename}' and '{self.folder_id}' in parents",
                fields="files(id, name)"
            ).execute()
            
            files = results.get("files", [])
            if not files:
                logger.warning(f"Config file not found, usando defaults")
                return {
                    "repositories": [
                        {"owner": "pandas-dev", "name": "pandas"},
                        {"owner": "microsoft", "name": "vscode"}
                    ],
                    "last_extraction": None
                }
            
            file_id = files[0]["id"]
            request = self.service.files().get_media(fileId=file_id)
            content = request.execute()
            
            config = json.loads(content.decode('utf-8'))
            logger.info(f"Config loaded from Drive: {filename}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to download config: {e}")
            return {
                "repositories": [
                    {"owner": "pandas-dev", "name": "pandas"},
                    {"owner": "microsoft", "name": "vscode"}
                ],
                "last_extraction": None
            }
    
    def upload_file(self, local_path: str, filename: str, folder_id: str = None):
        target_folder = folder_id or self.folder_id
        
        results = self.service.files().list(
            q=f"name = '{filename}' and '{target_folder}' in parents",
            fields="files(id)"
        ).execute()
        
        existing = results.get("files", [])
        
        with open(local_path, 'rb') as f:
            file_content = f.read()
        
        media = MediaIoBaseUpload(BytesIO(file_content), mimetype='text/csv')
        
        if existing:
            file_id = existing[0]['id']
            self.service.files().update(fileId=file_id, media_body=media).execute()
            logger.success(f"File updated: {filename}")
        else:
            file_metadata = {'name': filename, 'parents': [target_folder]}
            self.service.files().create(body=file_metadata, media_body=media).execute()
            logger.success(f"File created: {filename}")
