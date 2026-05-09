# src/domain/services/pipeline_service.py
"""Servicio de dominio - Lógica de negocio"""

from typing import List, Dict
from datetime import datetime
from src.domain.ports.github_client import GitHubClientPort
from src.domain.ports.database import DatabasePort
from src.domain.models import Repository, Issue, Commit


class PipelineService:
    """Servicio que orquesta la extracción de datos"""
    
    def __init__(self, github_client: GitHubClientPort, database: DatabasePort):
        self.github = github_client
        self.db = database
    
    def process_repository(self, owner: str, name: str, since: str=None) -> Dict:
        """Procesa un repositorio completo"""
        
        # 1. Insertar/actualizar repositorio
        repo_id = self.db.insert_repository(owner, name)
        
        # 2. Extraer y guardar issues
        issues_raw = list(self.github.get_issues(owner, name, since))
        issues = self._convert_to_issues(issues_raw, repo_id)
        issues_count = self.db.insert_issues(repo_id, issues)
        
        # 3. Extraer y guardar commits
        commits_raw = list(self.github.get_commits(owner, name, since))
        commits = self._convert_to_commits(commits_raw, repo_id)
        commits_count = self.db.insert_commits(repo_id, commits)
        
        return {
            "repository": f"{owner}/{name}",
            "issues_count": issues_count,
            "commits_count": commits_count,
            "timestamp": datetime.now().isoformat()
        }
    
    def _convert_to_issues(self, issues_raw: List[Dict], repo_id: int) -> List[Issue]:
        """Convierte JSON de GitHub a objetos Issue"""
        issues = []
        for i in issues_raw:
            if "pull_request" in i:  # Excluir PRs
                continue
            
            issues.append(Issue(
                id=i["id"],
                repo_id=repo_id,
                number=i["number"],
                title=i["title"],
                state=i["state"],
                created_at=datetime.fromisoformat(i["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(i["updated_at"].replace("Z", "+00:00")) if i.get("updated_at") else None,
                closed_at=datetime.fromisoformat(i["closed_at"].replace("Z", "+00:00")) if i.get("closed_at") else None,
                user_login=i.get("user", {}).get("login")
            ))
        return issues
    
    def _convert_to_commits(self, commits_raw: List[Dict], repo_id: int) -> List[Commit]:
        """Convierte JSON de GitHub a objetos Commit"""
        commits = []
        for c in commits_raw:
            commit_data = c.get("commit", {})
            author_data = commit_data.get("author", {})
            
            commits.append(Commit(
                sha=c["sha"],
                repo_id=repo_id,
                message=commit_data.get("message", ""),
                author_login=c.get("author", {}).get("login"),
                author_date=datetime.fromisoformat(author_data.get("date", "").replace("Z", "+00:00")) if author_data.get("date") else None
            ))
        return commits
