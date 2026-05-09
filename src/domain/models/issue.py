from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Issue:
    id: int
    repo_id: int
    number: int
    title: str
    state: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    user_login: Optional[str] = None
    extraction_date: datetime = None
    
    def __post_init__(self):
        if self.extraction_date is None:
            self.extraction_date = datetime.now()
