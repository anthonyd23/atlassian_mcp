import requests
import os
from ..common.auth import DataCenterAuth

class BitbucketDCProvider:
    def __init__(self):
        self.auth = DataCenterAuth()
        self.project = os.getenv('BITBUCKET_PROJECT', 'PROJECT')
    
    async def get_repository(self, repo_slug: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def list_repositories(self) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos"
            response = requests.get(url, headers=headers, params={'limit': 50})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def list_pull_requests(self, repo_slug: str, state: str = "OPEN") -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests"
            params = {'state': state, 'limit': 50}
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_pull_request(self, repo_slug: str, pr_id: int) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def create_pull_request(self, repo_slug: str, title: str, source_branch: str, dest_branch: str, description: str = "") -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests"
            payload = {
                "title": title,
                "fromRef": {"id": f"refs/heads/{source_branch}", "repository": {"slug": repo_slug, "project": {"key": self.project}}},
                "toRef": {"id": f"refs/heads/{dest_branch}", "repository": {"slug": repo_slug, "project": {"key": self.project}}},
                "description": description
            }
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_file_content(self, repo_slug: str, file_path: str, branch: str = "main") -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/browse/{file_path}"
            params = {'at': branch}
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            lines = response.json().get('lines', [])
            content = '\n'.join([line.get('text', '') for line in lines])
            return {'content': content, 'path': file_path}
        except Exception as e:
            return {'error': str(e)}
    
    async def list_commits(self, repo_slug: str, branch: str = "main") -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/commits"
            params = {'until': branch, 'limit': 50}
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_commit(self, repo_slug: str, commit_hash: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/commits/{commit_hash}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def list_branches(self, repo_slug: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/branches"
            response = requests.get(url, headers=headers, params={'limit': 50})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_pull_request_diff(self, repo_slug: str, pr_id: int) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}/diff"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return {'diff': response.text}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_pull_request_comments(self, repo_slug: str, pr_id: int) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}/activities"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def add_pr_comment(self, repo_slug: str, pr_id: int, comment: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}/comments"
            payload = {"text": comment}
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def approve_pull_request(self, repo_slug: str, pr_id: int) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}/approve"
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def merge_pull_request(self, repo_slug: str, pr_id: int) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            pr_url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}"
            pr_response = requests.get(pr_url, headers=headers)
            pr_response.raise_for_status()
            version = pr_response.json().get('version')
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}/merge"
            payload = {"version": version}
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_commit_diff(self, repo_slug: str, commit_hash: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/commits/{commit_hash}/diff"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return {'diff': response.text}
        except Exception as e:
            return {'error': str(e)}
    
    async def list_tags(self, repo_slug: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/tags"
            response = requests.get(url, headers=headers, params={'limit': 50})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def list_directory(self, repo_slug: str, path: str = "", branch: str = "main") -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/browse/{path}"
            params = {'at': branch}
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def update_pull_request(self, repo_slug: str, pr_id: int, title: str = None, description: str = None) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            pr_url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}"
            pr_response = requests.get(pr_url, headers=headers)
            pr_response.raise_for_status()
            pr_data = pr_response.json()
            payload = {"version": pr_data.get('version')}
            if title:
                payload["title"] = title
            if description:
                payload["description"] = description
            response = requests.put(pr_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def compare_commits(self, repo_slug: str, from_commit: str, to_commit: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/compare/diff"
            params = {'from': from_commit, 'to': to_commit}
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return {'diff': response.text}
        except Exception as e:
            return {'error': str(e)}
    
    async def search(self, query: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/1.0/projects/{self.project}/repos"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            repos = response.json().get('values', [])
            results = [{'type': 'repository', 'name': r.get('name'), 'slug': r.get('slug'), 'description': r.get('description')} 
                      for r in repos if query.lower() in r.get('name', '').lower()]
            return {'results': results}
        except Exception as e:
            return {'error': str(e)}
