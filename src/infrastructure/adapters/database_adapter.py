import psycopg2
from psycopg2 import pool
from psycopg2.extras import execute_values
from typing import List, Dict
import logging

from src.domain.ports.database import DatabasePort
from src.domain.models import Repository, Issue, Commit

logger = logging.getLogger(__name__)


class DatabaseAdapter(DatabasePort):
    """Implementación del adaptador de base de datos"""
    
    def __init__(self, host: str, user: str, password: str, database: str):
        self.pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            host=host,
            user=user,
            password=password,
            database=database
        )
        self._init_tables()
        logger.info(f"Database connected: {host}/{database}")
    
    def _init_tables(self):
        """Inicializa las tablas si no existen"""
        with self.pool.getconn() as conn:
            cur = conn.cursor()
            
            # Tabla de repositorios
            cur.execute("""
                CREATE TABLE IF NOT EXISTS repositories (
                    id SERIAL PRIMARY KEY,
                    owner VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(owner, name)
                )
            """)
            
            # Tabla de issues
            cur.execute("""
                CREATE TABLE IF NOT EXISTS issues (
                    id BIGINT PRIMARY KEY,
                    repo_id INTEGER REFERENCES repositories(id) ON DELETE CASCADE,
                    number INTEGER NOT NULL,
                    title TEXT,
                    state VARCHAR(50),
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    closed_at TIMESTAMP,
                    user_login VARCHAR(255),
                    extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de commits
            cur.execute("""
                CREATE TABLE IF NOT EXISTS commits (
                    sha VARCHAR(40) PRIMARY KEY,
                    repo_id INTEGER REFERENCES repositories(id) ON DELETE CASCADE,
                    message TEXT,
                    author_login VARCHAR(255),
                    author_date TIMESTAMP,
                    extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de control de extracciones
            cur.execute("""
                CREATE TABLE IF NOT EXISTS extraction_log (
                    id SERIAL PRIMARY KEY,
                    repo_id INTEGER REFERENCES repositories(id) ON DELETE CASCADE,
                    extraction_type VARCHAR(50),
                    record_count INTEGER,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Índices para mejor rendimiento
            cur.execute("CREATE INDEX IF NOT EXISTS idx_issues_repo ON issues(repo_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_commits_repo ON commits(repo_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_issues_state ON issues(state)")
            
            conn.commit()
            cur.close()
    
    def insert_repository(self, owner: str, name: str) -> int:
        """Inserta o actualiza repositorio - Idempotente"""
        with self.pool.getconn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO repositories (owner, name)
                VALUES (%(owner)s, %(name)s)
                ON CONFLICT (owner, name) DO UPDATE 
                SET name = EXCLUDED.name
                RETURNING id
            """, {"owner": owner, "name": name})
            result = cur.fetchone()
            conn.commit()
            cur.close()
            return result[0]
    
    def insert_issues(self, repo_id: int, issues: List[Issue]) -> int:
        """Inserta múltiples issues - Idempotente"""
        if not issues:
            return 0
        
        values = [
            (
                i.id, repo_id, i.number, i.title, i.state,
                i.created_at, i.updated_at, i.closed_at,
                i.user_login, i.extraction_date
            )
            for i in issues
        ]
        
        with self.pool.getconn() as conn:
            cur = conn.cursor()
            execute_values("""
                INSERT INTO issues (id, repo_id, number, title, state,
                                   created_at, updated_at, closed_at,
                                   user_login, extraction_date)
                VALUES %s
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    state = EXCLUDED.state,
                    updated_at = EXCLUDED.updated_at,
                    closed_at = EXCLUDED.closed_at
            """, values)
            conn.commit()
            cur.close()
            return len(issues)
    
    def insert_commits(self, repo_id: int, commits: List[Commit]) -> int:
        """Inserta múltiples commits - Idempotente"""
        if not commits:
            return 0
        
        values = [
            (
                c.sha, repo_id, c.message, c.author_login,
                c.author_date, c.extraction_date
            )
            for c in commits
        ]
        
        with self.pool.getconn() as conn:
            cur = conn.cursor()
            execute_values("""
                INSERT INTO commits (sha, repo_id, message, author_login,
                                   author_date, extraction_date)
                VALUES %s
                ON CONFLICT (sha) DO UPDATE SET
                    message = EXCLUDED.message,
                    author_login = EXCLUDED.author_login
            """, values)
            conn.commit()
            cur.close()
            return len(commits)
    
    def get_summary(self) -> List[Dict]:
        """Obtiene resumen de issues y commits por repositorio"""
        query = """
            SELECT 
                r.owner || '/' || r.name as repository,
                COUNT(DISTINCT i.id) as total_issues,
                COUNT(DISTINCT CASE WHEN i.state = 'open' THEN i.id END) as open_issues,
                COUNT(DISTINCT CASE WHEN i.state = 'closed' THEN i.id END) as closed_issues,
                COUNT(DISTINCT c.sha) as total_commits
            FROM repositories r
            LEFT JOIN issues i ON r.id = i.repo_id
            LEFT JOIN commits c ON r.id = c.repo_id
            GROUP BY r.id, r.owner, r.name
            ORDER BY r.name
        """
        
        with self.pool.getconn() as conn:
            cur = conn.cursor()
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            results = [dict(zip(columns, row)) for row in cur.fetchall()]
            cur.close()
            return results
    
    def log_extraction(self, repo_id: int, extraction_type: str, record_count: int):
        """Registra una extracción"""
        with self.pool.getconn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO extraction_log (repo_id, extraction_type, record_count)
                VALUES (%s, %s, %s)
            """, (repo_id, extraction_type, record_count))
            conn.commit()
            cur.close()
    
    def close(self):
        """Cierra el pool de conexiones"""
        self.pool.closeall()
        logger.info("Database connection closed")
