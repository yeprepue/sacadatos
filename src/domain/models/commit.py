# src/domain/models/commit.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Commit:
    sha: str
    repo_id: int
    message: str
    author_login: Optional[str] = None
    author_date: Optional[datetime] = None
    extraction_date: datetime = None
    
    def __post_init__(self):
        if self.extraction_date is None:
            self.extraction_date = datetime.now()
