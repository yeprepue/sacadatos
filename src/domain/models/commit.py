from sqlmodel import SQLModel, Field, Column
from typing import Optional
from datetime import datetime
from sqlalchemy import BigInteger, ForeignKey

class Commit(SQLModel, table=True):
    __tablename__ = "commits"
    
    sha: str = Field(primary_key=True, max_length=40)
    repo_id: int = Field(sa_column=Column(BigInteger, ForeignKey("repositories.id"), index=True))
    message: str
    author_login: Optional[str] = None
    author_date: Optional[datetime] = None
    extraction_date: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True
