from abc import ABC, abstractmethod
from typing import Dict

class DriveClientPort(ABC):
    """Puerto para Google Drive - Interfaz"""
    
    @abstractmethod
    def download_config(self, filename: str) -> Dict:
        pass
    
    @abstractmethod
    def upload_file(self, local_path: str, filename: str, folder_id: str):
        pass
