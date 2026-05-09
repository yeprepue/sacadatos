import requests
from datetime import datetime
from typing import List, Dict


class GitHubExtractor:

    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_all_issues(self, owner: str, repo: str, since: str=None) -> List[Dict]:
        """Extrae issues - incremental o total"""
        issues = []
        page = 1
        
        while True:
            url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            params = {
                "state": "all",
                "per_page": 100,
                "page": page
            }
            if since:
                params["since"] = since
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                break
                
            data = response.json()
            if not data:
                break
                
            issues.extend(data)
            page += 1
            
        return issues

    def get_all_commits(self, owner: str, repo: str, since: str=None) -> List[Dict]:
        """Extrae commits - incremental o total"""
        commits = []
        page = 1
        
        while True:
            url = f"{self.base_url}/repos/{owner}/{repo}/commits"
            params = {"per_page": 100, "page": page}
            if since:
                params["since"] = since
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                break
                
            data = response.json()
            if not data:
                break
                
            commits.extend(data)
            page += 1
            
        return commits

    def extract_full(self, owner: str, repo: str) -> Dict:
        """Extracción total"""
        return {
            "issues": self.get_all_issues(owner, repo),
            "commits": self.get_all_commits(owner, repo),
            "extraction_type": "full"
        }

    def extract_incremental(self, owner: str, repo: str, last_extraction: str) -> Dict:
        """Extracción incremental"""
        return {
            "issues": self.get_all_issues(owner, repo, since=last_extraction),
            "commits": self.get_all_commits(owner, repo, since=last_extraction),
            "extraction_type": "incremental"
        }
