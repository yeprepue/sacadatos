from abc import ABC, abstractmethod
from typing import List, Dict

class DatabasePort(ABC):
    @abstractmethod
    def insert_repository(self, owner: str, name: str) -> int:
        pass
    
    @abstractmethod
    def insert_issues(self, repo_id: int, issues: List) -> int:
        pass
    
    @abstractmethod
    def insert_commits(self, repo_id: int, commits: List) -> int:
        pass
    
    @abstractmethod
    def get_summary(self) -> List[Dict]:
        pass
    
    @abstractmethod
    def close(self):
        pass
