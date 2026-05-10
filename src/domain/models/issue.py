from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Issue(SQLModel, table=True):
    __tablename__ = "issues"
    
    id: int = Field(primary_key=True)
    repo_id: int = Field(foreign_key="repositories.id", index=True)
    number: int
    title: str
    state: str = Field(index=True)
    created_at: datetime
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    user_login: Optional[str] = None
    extraction_date: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True
