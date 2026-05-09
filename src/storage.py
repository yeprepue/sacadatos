import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime


class DataStorage:

    def __init__(self, host: str, user: str, password: str, db: str):
        self.conn = psycopg2.connect(
            host=host, user=user, password=password, database=db
        )
        self.create_tables()

    def create_tables(self):
        """Crea tablas normalizadas"""
        with self.conn.cursor() as cur:
            # Tabla de repositorios
            cur.execute("""
                CREATE TABLE IF NOT EXISTS repositories (
                    id SERIAL PRIMARY KEY,
                    owner VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    UNIQUE(owner, name)
                )
            """)
            
            # Tabla de issues
            cur.execute("""
                CREATE TABLE IF NOT EXISTS issues (
                    id BIGINT PRIMARY KEY,
                    repo_id INTEGER REFERENCES repositories(id),
                    number INTEGER,
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
                    repo_id INTEGER REFERENCES repositories(id),
                    message TEXT,
                    author_login VARCHAR(255),
                    author_date TIMESTAMP,
                    created_at TIMESTAMP,
                    extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de control de extracciones
            cur.execute("""
                CREATE TABLE IF NOT EXISTS extraction_log (
                    id SERIAL PRIMARY KEY,
                    repo_id INTEGER REFERENCES repositories(id),
                    extraction_type VARCHAR(50),
                    record_count INTEGER,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.conn.commit()

    def insert_repository(self, owner: str, name: str) -> int:
        """Inserta repositorio y retorna su ID (idempotente)"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO repositories (owner, name)
                VALUES (%s, %s)
                ON CONFLICT (owner, name) DO UPDATE 
                SET owner = EXCLUDED.owner
                RETURNING id
            """, (owner, name))
            self.conn.commit()
            return cur.fetchone()[0]

    def insert_issues(self, repo_id: int, issues: List[dict]):
        """Inserta issues (idempotente)"""
        with self.conn.cursor() as cur:
            data = [
                (
                    i['id'], repo_id, i.get('number'), i.get('title'),
                    i.get('state'), i.get('created_at'), i.get('updated_at'),
                    i.get('closed_at'), i.get('user', {}).get('login')
                )
                for i in issues
                if 'pull_request' not in i  # Excluir PRs de issues
            ]
            
            if data:
                execute_values("""
                    INSERT INTO issues (id, repo_id, number, title, state, 
                                       created_at, updated_at, closed_at, user_login)
                    VALUES %s
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        state = EXCLUDED.state,
                        updated_at = EXCLUDED.updated_at
                """, data)
                self.conn.commit()

    def insert_commits(self, repo_id: int, commits: List[dict]):
        """Inserta commits (idempotente)"""
        with self.conn.cursor() as cur:
            data = [
                (
                    c['sha'], repo_id, c.get('commit', {}).get('message'),
                    c.get('author', {}).get('login'),
                    c.get('commit', {}).get('author', {}).get('date'),
                    datetime.now()
                )
                for c in commits
            ]
            
            if data:
                execute_values("""
                    INSERT INTO commits (sha, repo_id, message, author_login, 
                                        author_date, created_at)
                    VALUES %s
                    ON CONFLICT (sha) DO UPDATE SET
                        message = EXCLUDED.message
                """, data)
                self.conn.commit()

    def log_extraction(self, repo_id: int, extraction_type: str, count: int):
        """Registra la extracción"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO extraction_log (repo_id, extraction_type, record_count)
                VALUES (%s, %s, %s)
            """, (repo_id, extraction_type, count))
            self.conn.commit()
