from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, BigInteger

class Repository(SQLModel, table=True):
    __tablename__ = "repositories"
    
    id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True))
    owner: str = Field(index=True)
    name: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        unique_together = ("owner", "name")
