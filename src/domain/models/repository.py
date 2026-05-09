from dataclasses import dataclass
from typing import Optional

@dataclass
class Repository:
    id: Optional[int] = None
    owner: str = ""
    name: str = ""
    
    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.name}"
