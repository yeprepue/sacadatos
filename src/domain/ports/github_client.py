from abc import ABC, abstractmethod
from typing import Iterator, Dict

class GitHubClientPort(ABC):
    @abstractmethod
    def get_issues(self, owner: str, repo: str, since: str = None) -> Iterator[Dict]:
        pass
    
    @abstractmethod
    def get_commits(self, owner: str, repo: str, since: str = None) -> Iterator[Dict]:
        pass
