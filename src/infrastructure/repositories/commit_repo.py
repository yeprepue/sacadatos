from typing import List
from sqlmodel import select, func
from src.infrastructure.database import Database
from src.domain.models import Commit as CommitModel


class CommitRepository:
    def __init__(self, db: Database):
        self.db = db
    
    def bulk_insert(self, repo_id: int, commits: List[CommitModel]) -> int:
        if not commits:
            return 0
        
        with self.db.get_session() as session:
            for commit in commits:
                commit.repo_id = repo_id
            
            session.bulk_save_objects(commits, upsert=True)
            session.commit()
            return len(commits)
    
    def count_by_repo(self, repo_id: int) -> int:
        with self.db.get_session() as session:
            return session.exec(
                select(func.count()).select_from(CommitModel).where(CommitModel.repo_id == repo_id)
            ).one()
