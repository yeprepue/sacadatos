from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from contextlib import contextmanager
from src.config.settings import DatabaseConfig
from src.config.logging_config import logger


class Database:

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.engine = create_engine(connection_string, echo=False)
        self._create_tables()
        logger.info(f"Database connected: {connection_string}")
    
    def _create_tables(self):
        """Crea las tablas automáticamente"""
        from src.domain.models import Repository, Issue, Commit
        SQLModel.metadata.create_all(self.engine)
        logger.info("Tables created/verified")
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def close(self):
        self.engine.dispose()
        logger.info("Database connection closed")
