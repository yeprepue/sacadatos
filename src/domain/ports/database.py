from abc import ABC, abstractmethod
from typing import List, Dict
from src.domain.models import Repository, Issue, Commit

class DatabasePort(ABC):
    """Puerto para base de datos - Interfaz"""
    
    @abstractmethod
    def insert_repository(self, owner: str, name: str) -> int:
        pass
    
    @abstractmethod
    def insert_issues(self, repo_id: int, issues: List[Issue]) -> int:
        pass
    
    @abstractmethod
    def insert_commits(self, repo_id: int, commits: List[Commit]) -> int:
        pass
    
    @abstractmethod
    def get_summary(self) -> List[Dict]:
        pass
    
    @abstractmethod
    def close(self):
        pass
