from typing import List
from sqlmodel import select
from src.infrastructure.database import Database
from src.domain.models import Repository as RepositoryModel


class RepositoryRepository:

    def __init__(self, db: Database):
        self.db = db
    
    def upsert(self, owner: str, name: str) -> int:
        with self.db.get_session() as session:
            repo = session.exec(
                select(RepositoryModel).where(
                    RepositoryModel.owner == owner,
                    RepositoryModel.name == name
                )
            ).first()
            
            if repo:
                return repo.id
            
            repo = RepositoryModel(owner=owner, name=name)
            session.add(repo)
            session.commit()
            session.refresh(repo)
            return repo.id
    
    def get_all(self) -> List[RepositoryModel]:
        with self.db.get_session() as session:
            return list(session.exec(select(RepositoryModel)).all())
