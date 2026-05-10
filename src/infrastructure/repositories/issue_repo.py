from typing import List
from sqlmodel import select, func
from src.infrastructure.database import Database
from src.domain.models import Issue as IssueModel


class IssueRepository:
    def __init__(self, db: Database):
        self.db = db
    
    def bulk_insert(self, repo_id: int, issues: List[IssueModel]) -> int:
        if not issues:
            return 0
        
        inserted = 0
        with self.db.get_session() as session:
            for issue in issues:
                issue.repo_id = repo_id
                try:
                    existing = session.get(IssueModel, issue.id)
                    if existing:
                        existing.title = issue.title
                        existing.state = issue.state
                        existing.updated_at = issue.updated_at
                        existing.closed_at = issue.closed_at
                    else:
                        session.add(issue)
                    inserted += 1
                except Exception as e:
                    print(f"Error inserting issue {issue.id}: {e}")
                    continue
            session.commit()
            return inserted
    
    def count_by_repo(self, repo_id: int) -> dict:
        with self.db.get_session() as session:
            total = session.exec(
                select(func.count()).select_from(IssueModel).where(IssueModel.repo_id == repo_id)
            ).one()
            
            open_ = session.exec(
                select(func.count()).select_from(IssueModel).where(
                    IssueModel.repo_id == repo_id,
                    IssueModel.state == "open"
                )
            ).one()
            
            closed = session.exec(
                select(func.count()).select_from(IssueModel).where(
                    IssueModel.repo_id == repo_id,
                    IssueModel.state == "closed"
                )
            ).one()
            
            return {"total": total, "open": open_, "closed": closed}
