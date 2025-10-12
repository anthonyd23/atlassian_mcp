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
            # Bitbucket Cloud API for personal accounts
            url = "https://api.bitbucket.org/2.0/repositories"
            
            # Use username from auth for Bitbucket Cloud
            username = self.auth.username.split('@')[0]
            url = f"https://api.bitbucket.org/2.0/repositories/{username}"
            
            response = requests.get(url, auth=(self.auth.username, self.auth.api_token))
            response.raise_for_status()
            
            repos = response.json().get('values', [])
            results = []
            
            for repo in repos:
                if query.lower() in repo.get('name', '').lower():
                    results.append({
                        'type': 'repository',
                        'name': repo.get('name'),
                        'full_name': repo.get('full_name'),
                        'description': repo.get('description')
                    })
            
            return {'results': results}
        except Exception as e:
            return {'error': str(e)}
    
    async def _get_repositories(self) -> str:
        try:
            username = self.auth.username.split('@')[0]
            url = f"https://api.bitbucket.org/2.0/repositories/{username}"
            
            response = requests.get(url, auth=(self.auth.username, self.auth.api_token), params={'pagelen': 25})
            response.raise_for_status()
            
            repos = response.json().get('values', [])
            return json.dumps(repos, indent=2)
        except Exception as e:
            return f"Error fetching repositories: {str(e)}"
    
    async def _get_pull_requests(self, repo: str) -> str:
        try:
            username = self.auth.username.split('@')[0]
            url = f"https://api.bitbucket.org/2.0/repositories/{username}/{repo}/pullrequests"
            
            response = requests.get(url, auth=(self.auth.username, self.auth.api_token), params={'pagelen': 25})
            response.raise_for_status()
            
            prs = response.json().get('values', [])
            return json.dumps(prs, indent=2)
        except Exception as e:
            return f"Error fetching pull requests: {str(e)}"
