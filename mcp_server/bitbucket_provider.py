import requests
import json
import os
from .auth import Auth

class BitbucketProvider:
    def __init__(self):
        self.auth = Auth()
        self.bitbucket_token = os.getenv('BITBUCKET_API_TOKEN', self.auth.api_token)
        self.workspace = os.getenv('BITBUCKET_WORKSPACE', self.auth.username.split('@')[0])
    
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
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}"
            
            response = requests.get(url, auth=(self.auth.username, self.bitbucket_token))
            
            if response.status_code == 401:
                return {
                    'error': 'Bitbucket authentication failed',
                    'note': 'Create token at https://bitbucket.org/account/settings/api-tokens/ and set BITBUCKET_API_TOKEN',
                    'results': []
                }
            
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
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}"
            
            response = requests.get(url, auth=(self.auth.username, self.bitbucket_token), params={'pagelen': 25})
            response.raise_for_status()
            
            repos = response.json().get('values', [])
            return json.dumps(repos, indent=2)
        except Exception as e:
            return f"Error fetching repositories: {str(e)}"
    
    async def _get_pull_requests(self, repo: str) -> str:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo}/pullrequests"
            
            response = requests.get(url, auth=(self.auth.username, self.bitbucket_token), params={'pagelen': 25})
            response.raise_for_status()
            
            prs = response.json().get('values', [])
            return json.dumps(prs, indent=2)
        except Exception as e:
            return f"Error fetching pull requests: {str(e)}"
