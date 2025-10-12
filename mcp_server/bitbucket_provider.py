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
    
    async def get_repository(self, repo_slug: str) -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}"
            response = requests.get(url, auth=(self.auth.username, self.bitbucket_token))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def list_repositories(self) -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}"
            response = requests.get(url, auth=(self.auth.username, self.bitbucket_token), params={'pagelen': 50})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def list_pull_requests(self, repo_slug: str, state: str = "OPEN") -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/pullrequests"
            params = {'state': state, 'pagelen': 50}
            response = requests.get(url, auth=(self.auth.username, self.bitbucket_token), params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_pull_request(self, repo_slug: str, pr_id: int) -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/pullrequests/{pr_id}"
            response = requests.get(url, auth=(self.auth.username, self.bitbucket_token))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def create_pull_request(self, repo_slug: str, title: str, source_branch: str, dest_branch: str, description: str = "") -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/pullrequests"
            payload = {
                "title": title,
                "source": {"branch": {"name": source_branch}},
                "destination": {"branch": {"name": dest_branch}},
                "description": description
            }
            response = requests.post(url, auth=(self.auth.username, self.bitbucket_token), json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_file_content(self, repo_slug: str, file_path: str, branch: str = "main") -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/src/{branch}/{file_path}"
            response = requests.get(url, auth=(self.auth.username, self.bitbucket_token))
            response.raise_for_status()
            return {'content': response.text, 'path': file_path}
        except Exception as e:
            return {'error': str(e)}
    
    async def list_commits(self, repo_slug: str, branch: str = "main") -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/commits/{branch}"
            response = requests.get(url, auth=(self.auth.username, self.bitbucket_token), params={'pagelen': 50})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_commit(self, repo_slug: str, commit_hash: str) -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/commit/{commit_hash}"
            response = requests.get(url, auth=(self.auth.username, self.bitbucket_token))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def list_branches(self, repo_slug: str) -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/refs/branches"
            response = requests.get(url, auth=(self.auth.username, self.bitbucket_token), params={'pagelen': 50})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_pull_request_diff(self, repo_slug: str, pr_id: int) -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/pullrequests/{pr_id}/diff"
            response = requests.get(url, auth=(self.auth.username, self.bitbucket_token))
            response.raise_for_status()
            return {'diff': response.text}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_pull_request_comments(self, repo_slug: str, pr_id: int) -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/pullrequests/{pr_id}/comments"
            response = requests.get(url, auth=(self.auth.username, self.bitbucket_token))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def add_pr_comment(self, repo_slug: str, pr_id: int, comment: str) -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/pullrequests/{pr_id}/comments"
            payload = {"content": {"raw": comment}}
            response = requests.post(url, auth=(self.auth.username, self.bitbucket_token), json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def approve_pull_request(self, repo_slug: str, pr_id: int) -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/pullrequests/{pr_id}/approve"
            response = requests.post(url, auth=(self.auth.username, self.bitbucket_token))
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def merge_pull_request(self, repo_slug: str, pr_id: int) -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/pullrequests/{pr_id}/merge"
            response = requests.post(url, auth=(self.auth.username, self.bitbucket_token))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_commit_diff(self, repo_slug: str, commit_hash: str) -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/diff/{commit_hash}"
            response = requests.get(url, auth=(self.auth.username, self.bitbucket_token))
            response.raise_for_status()
            return {'diff': response.text}
        except Exception as e:
            return {'error': str(e)}
    
    async def list_tags(self, repo_slug: str) -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/refs/tags"
            response = requests.get(url, auth=(self.auth.username, self.bitbucket_token), params={'pagelen': 50})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def list_directory(self, repo_slug: str, path: str = "", branch: str = "main") -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/src/{branch}/{path}"
            response = requests.get(url, auth=(self.auth.username, self.bitbucket_token))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def update_pull_request(self, repo_slug: str, pr_id: int, title: str = None, description: str = None) -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/pullrequests/{pr_id}"
            payload = {}
            if title:
                payload["title"] = title
            if description:
                payload["description"] = description
            response = requests.put(url, auth=(self.auth.username, self.bitbucket_token), json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def compare_commits(self, repo_slug: str, from_commit: str, to_commit: str) -> dict:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/diff/{from_commit}..{to_commit}"
            response = requests.get(url, auth=(self.auth.username, self.bitbucket_token))
            response.raise_for_status()
            return {'diff': response.text}
        except Exception as e:
            return {'error': str(e)}
    
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
