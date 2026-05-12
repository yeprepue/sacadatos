import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class RepositoryConfig:
    owner: str
    name: str


@dataclass
class DatabaseConfig:
    host: str = os.getenv("POSTGRES_HOST", "postgres")
    port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    user: str = os.getenv("POSTGRES_USER", "postgres")
    password: str = os.getenv("POSTGRES_PASSWORD", "admin")
    database: str = os.getenv("POSTGRES_DB", "sacadatos")
    
    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class GitHubConfig:
    token: str = os.getenv("GITHUB_TOKEN", "")


@dataclass
class GoogleDriveConfig:
    credentials_path: Path = Path(os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"))
    folder_id: str = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
    config_file_id: str = os.getenv("GOOGLE_DRIVE_CONFIG_FILE_ID", "")


@dataclass
class PipelineConfig:
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    github: GitHubConfig = field(default_factory=GitHubConfig)
    google_drive: GoogleDriveConfig = field(default_factory=GoogleDriveConfig)
    repositories: List[RepositoryConfig] = field(default_factory=list)
    last_extraction: Optional[str] = None
    extraction_type: str = "full"
