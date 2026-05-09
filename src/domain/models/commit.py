# src/domain/models/commit.py
"""Modelo de dominio - Commit"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Commit(SQLModel, table=True):
    __tablename__ = "commits"
    
    sha: str = Field(primary_key=True, max_length=40)
    repo_id: int = Field(foreign_key="repositories.id", index=True)
    message: str
    author_login: Optional[str] = None
    author_date: Optional[datetime] = None
    extraction_date: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True
