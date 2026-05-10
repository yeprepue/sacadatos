import logging
from typing import List, Dict
from datetime import datetime
from src.domain.ports.github_client import GitHubClientPort
from src.domain.ports.database import DatabasePort
from src.domain.services.pipeline_service import PipelineService
from src.config.logging_config import logger

class ExtractGitHubDataUseCase:
    def __init__(self, github_client: GitHubClientPort, database: DatabasePort):
        self.service = PipelineService(github_client, database)
    
    def execute(self, repositories: List[Dict], since: str = None) -> Dict:
        logger.info(f"Iniciando extracción para {len(repositories)} repositorios")
        start_time = datetime.now()
        
        results = []
        
        for repo in repositories:
            owner = repo.get("owner")
            name = repo.get("name")
            
            if not owner or not name:
                logger.warning(f"Configuración inválida: {repo}")
                continue
            
            try:
                result = self.service.process_repository(owner, name, since)
                results.append(result)
            except Exception as e:
                logger.error(f"Error procesando {owner}/{name}: {e}")
                results.append({
                    "repository": f"{owner}/{name}",
                    "error": str(e),
                    "status": "failed"
                })
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            "status": "completed",
            "duration_seconds": duration,
            "total_repositories": len(repositories),
            "successful": len([r for r in results if "error" not in r]),
            "failed": len([r for r in results if "error" in r]),
            "results": results
        }
