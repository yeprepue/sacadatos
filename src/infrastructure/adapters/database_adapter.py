from typing import List, Dict
from src.domain.ports.database import DatabasePort
from src.infrastructure.database import Database
from src.infrastructure.repositories.repository_repo import RepositoryRepository
from src.infrastructure.repositories.issue_repo import IssueRepository
from src.infrastructure.repositories.commit_repo import CommitRepository
from src.config.logging_config import logger


class DatabaseAdapter(DatabasePort):
    def __init__(self, db: Database):
        self.db = db
        self.repo_repo = RepositoryRepository(db)
        self.issue_repo = IssueRepository(db)
        self.commit_repo = CommitRepository(db)
    
    def insert_repository(self, owner: str, name: str) -> int:
        return self.repo_repo.upsert(owner, name)
    
    def insert_issues(self, repo_id: int, issues: List) -> int:
        return self.issue_repo.bulk_insert(repo_id, issues)
    
    def insert_commits(self, repo_id: int, commits: List) -> int:
        return self.commit_repo.bulk_insert(repo_id, commits)
    
    def get_summary(self) -> List[Dict]:
        repos = self.repo_repo.get_all()
        summary = []
        
        for repo in repos:
            issues_stats = self.issue_repo.count_by_repo(repo.id)
            commits_count = self.commit_repo.count_by_repo(repo.id)
            
            summary.append({
                "repository": f"{repo.owner}/{repo.name}",
                "total_issues": issues_stats["total"],
                "open_issues": issues_stats["open"],
                "closed_issues": issues_stats["closed"],
                "total_commits": commits_count
            })
        
        return summary
    
    def close(self):
        self.db.close()
