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
