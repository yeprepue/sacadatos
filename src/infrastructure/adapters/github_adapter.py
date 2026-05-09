# src/infrastructure/adapters/github_adapter.py
"""Adaptador de GitHub API - Implementación del puerto"""

import requests
from typing import Iterator, Dict
import logging

from src.domain.ports.github_client import GitHubClientPort

logger = logging.getLogger(__name__)


class GitHubAPIError(Exception):
    """Excepción personalizada para errores de GitHub API"""
    pass


class GitHubAdapter(GitHubClientPort):
    """Implementación del cliente de GitHub"""
    
    BASE_URL = "https://api.github.com"
    MAX_PER_PAGE = 100
    
    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        })
        self._rate_limit_remaining = 0
    
    @property
    def rate_limit(self) -> int:
        return self._rate_limit_remaining
    
    def _request(self, endpoint: str, params: dict = None) -> list:
        """Realiza request a la API"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params)
            self._rate_limit_remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
            
            if response.status_code == 404:
                logger.warning(f"Resource not found: {endpoint}")
                return []
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise GitHubAPIError(str(e))
    
    def get_issues(self, owner: str, repo: str, since: str = None) -> Iterator[Dict]:
        """Obtiene todos los issues (paginado)"""
        page = 1
        
        while True:
            params = {
                "state": "all",
                "per_page": self.MAX_PER_PAGE,
                "page": page,
                "sort": "updated",
                "direction": "desc"
            }
            
            if since:
                params["since"] = since
            
            data = self._request(f"repos/{owner}/{repo}/issues", params)
            
            if not data:
                break
            
            # Filtrar solo issues (no pull requests)
            issues = [item for item in data if "pull_request" not in item]
            
            yield from issues
            
            if len(data) < self.MAX_PER_PAGE:
                break
            
            page += 1
    
    def get_commits(self, owner: str, repo: str, since: str = None) -> Iterator[Dict]:
        """Obtiene todos los commits (paginado)"""
        page = 1
        
        while True:
            params = {
                "per_page": self.MAX_PER_PAGE,
                "page": page
            }
            
            if since:
                params["since"] = since
            
            data = self._request(f"repos/{owner}/{repo}/commits", params)
            
            if not data:
                break
            
            yield from data
            
            if len(data) < self.MAX_PER_PAGE:
                break
            
            page += 1
    
    def close(self):
        """Cierra la sesión"""
        self.session.close()
