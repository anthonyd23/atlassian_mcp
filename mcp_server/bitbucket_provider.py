import requests
import json
from .auth import Auth

class BitbucketProvider:
    def __init__(self):
        self.auth = Auth()
    
    async def get_resource(self, uri: str) -> str:
        if uri == "atlassian://bitbucket/repositories":
            return await self._get_repositories()
        elif "/pullrequests" in uri:
            repo = uri.split("/")[-2]
            return await self._get_pull_requests(repo)
        else:
            raise ValueError(f"Unknown Bitbucket resource: {uri}")
    
    async def search(self, query: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects"
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            projects = response.json().get('values', [])
            results = []
            
            for project in projects:
                if query.lower() in project.get('name', '').lower():
                    results.append({
                        'type': 'project',
                        'key': project.get('key'),
                        'name': project.get('name'),
                        'description': project.get('description')
                    })
            
            return {'results': results}
        except Exception as e:
            return {'error': str(e)}
    
    async def _get_repositories(self) -> str:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/repos"
            
            response = requests.get(url, headers=headers, params={'limit': 25})
            response.raise_for_status()
            
            repos = response.json().get('values', [])
            return json.dumps(repos, indent=2)
        except Exception as e:
            return f"Error fetching repositories: {str(e)}"
    
    async def _get_pull_requests(self, repo: str) -> str:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{repo}/repos/{repo}/pull-requests"
            
            response = requests.get(url, headers=headers, params={'limit': 25})
            response.raise_for_status()
            
            prs = response.json().get('values', [])
            return json.dumps(prs, indent=2)
        except Exception as e:
            return f"Error fetching pull requests: {str(e)}"
