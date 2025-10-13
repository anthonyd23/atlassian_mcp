import requests
import json
import os
import logging
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ..common.auth import Auth
from ..common.validation import validate_repo_slug, validate_pr_id, validate_non_empty, validate_path, validate_branch_name, validate_commit_hash, sanitize_url_path

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 25
LIST_PAGE_SIZE = 50

class BitbucketProvider:
    def __init__(self) -> None:
        self.auth = Auth()
        self.bitbucket_token = os.getenv('BITBUCKET_API_TOKEN')
        self.workspace = os.getenv('BITBUCKET_WORKSPACE')
        self.session = self._create_session()
        self.timeout = 25
        
        if self.bitbucket_token and self.workspace:
            logger.info(f"BitbucketProvider initialized for workspace: {self.workspace}")
    
    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET", "POST", "PUT", "DELETE"])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    async def get_resource(self, uri: str) -> str:
        if uri == "atlassian://bitbucket/repositories":
            return await self._get_repositories()
        elif "/pullrequests" in uri:
            repo = uri.split("/")[-2]
            return await self._get_pull_requests(repo)
        else:
            raise ValueError(f"Unknown Bitbucket resource: {uri}")
    
    async def get_repository(self, repo_slug: str) -> Dict[str, Any]:
        """Get detailed repository information."""
        valid, error = validate_repo_slug(repo_slug)
        if not valid:
            logger.warning(f"Invalid repo_slug: {repo_slug}")
            return {'error': error}
        try:
            logger.info(f"Fetching repository: {repo_slug}")
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{sanitize_url_path(repo_slug)}"
            response = self.session.get(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching repository {repo_slug}: {e}")
            return {'error': str(e)}
    
    async def list_repositories(self) -> Dict[str, Any]:
        """List all repositories in workspace."""
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}"
            response = self.session.get(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout, params={'pagelen': LIST_PAGE_SIZE})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def list_pull_requests(self, repo_slug: str, state: str = "OPEN") -> Dict[str, Any]:
        """List pull requests with optional state filter."""
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/pullrequests"
            params = {'state': state, 'pagelen': LIST_PAGE_SIZE}
            response = self.session.get(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_pull_request(self, repo_slug: str, pr_id: int) -> Dict[str, Any]:
        """Get detailed pull request information."""
        valid, error = validate_repo_slug(repo_slug)
        if not valid:
            return {'error': error}
        valid, error = validate_pr_id(pr_id)
        if not valid:
            return {'error': error}
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/pullrequests/{pr_id}"
            response = self.session.get(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def create_pull_request(self, repo_slug: str, title: str, source_branch: str, dest_branch: str, description: str = "") -> Dict[str, Any]:
        """Create a new pull request."""
        valid, error = validate_repo_slug(repo_slug)
        if not valid:
            return {'error': error}
        valid, error = validate_non_empty(title, "title")
        if not valid:
            return {'error': error}
        valid, error = validate_non_empty(source_branch, "source_branch")
        if not valid:
            return {'error': error}
        valid, error = validate_non_empty(dest_branch, "dest_branch")
        if not valid:
            return {'error': error}
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/pullrequests"
            payload = {
                "title": title,
                "source": {"branch": {"name": source_branch}},
                "destination": {"branch": {"name": dest_branch}},
                "description": description
            }
            response = self.session.post(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_file_content(self, repo_slug: str, file_path: str, branch: str = "main") -> Dict[str, Any]:
        """Get raw content of a file."""
        valid, error = validate_path(file_path, "file_path")
        if not valid:
            return {'error': error}
        valid, error = validate_branch_name(branch)
        if not valid:
            return {'error': error}
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{sanitize_url_path(repo_slug)}/src/{sanitize_url_path(branch)}/{sanitize_url_path(file_path)}"
            response = self.session.get(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout)
            response.raise_for_status()
            return {'content': response.text, 'path': file_path}
        except Exception as e:
            return {'error': str(e)}
    
    async def list_commits(self, repo_slug: str, branch: str = "main") -> Dict[str, Any]:
        """List commits in a branch."""
        valid, error = validate_branch_name(branch)
        if not valid:
            return {'error': error}
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{sanitize_url_path(repo_slug)}/commits/{sanitize_url_path(branch)}"
            response = self.session.get(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout, params={'pagelen': LIST_PAGE_SIZE})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_commit(self, repo_slug: str, commit_hash: str) -> Dict[str, Any]:
        """Get detailed information about a commit."""
        valid, error = validate_commit_hash(commit_hash)
        if not valid:
            return {'error': error}
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{sanitize_url_path(repo_slug)}/commit/{commit_hash}"
            response = self.session.get(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def list_branches(self, repo_slug: str) -> Dict[str, Any]:
        """List all branches in a repository."""
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/refs/branches"
            response = self.session.get(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout, params={'pagelen': LIST_PAGE_SIZE})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_pull_request_diff(self, repo_slug: str, pr_id: int) -> Dict[str, Any]:
        """Get the full diff for a pull request."""
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/pullrequests/{pr_id}/diff"
            response = self.session.get(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout)
            response.raise_for_status()
            return {'diff': response.text}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_pull_request_comments(self, repo_slug: str, pr_id: int) -> Dict[str, Any]:
        """Retrieve all comments on a pull request."""
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/pullrequests/{pr_id}/comments"
            response = self.session.get(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def add_pr_comment(self, repo_slug: str, pr_id: int, comment: str) -> Dict[str, Any]:
        """Add a comment to a pull request."""
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/pullrequests/{pr_id}/comments"
            payload = {"content": {"raw": comment}}
            response = self.session.post(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def approve_pull_request(self, repo_slug: str, pr_id: int) -> Dict[str, Any]:
        """Approve a pull request."""
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/pullrequests/{pr_id}/approve"
            response = self.session.post(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def merge_pull_request(self, repo_slug: str, pr_id: int) -> Dict[str, Any]:
        """Merge an approved pull request."""
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/pullrequests/{pr_id}/merge"
            response = self.session.post(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_commit_diff(self, repo_slug: str, commit_hash: str) -> Dict[str, Any]:
        """Get the diff/changes for a commit."""
        valid, error = validate_commit_hash(commit_hash)
        if not valid:
            return {'error': error}
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{sanitize_url_path(repo_slug)}/diff/{commit_hash}"
            response = self.session.get(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout)
            response.raise_for_status()
            return {'diff': response.text}
        except Exception as e:
            return {'error': str(e)}
    
    async def list_tags(self, repo_slug: str) -> Dict[str, Any]:
        """List all tags in a repository."""
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/refs/tags"
            response = self.session.get(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout, params={'pagelen': LIST_PAGE_SIZE})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def list_directory(self, repo_slug: str, path: str = "", branch: str = "main") -> Dict[str, Any]:
        """List files and folders in a directory path."""
        valid, error = validate_path(path, "path")
        if not valid:
            return {'error': error}
        valid, error = validate_branch_name(branch)
        if not valid:
            return {'error': error}
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{sanitize_url_path(repo_slug)}/src/{sanitize_url_path(branch)}/{sanitize_url_path(path)}"
            response = self.session.get(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def update_pull_request(self, repo_slug: str, pr_id: int, title: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """Update pull request title or description."""
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo_slug}/pullrequests/{pr_id}"
            payload = {}
            if title:
                payload["title"] = title
            if description:
                payload["description"] = description
            response = self.session.put(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def compare_commits(self, repo_slug: str, from_commit: str, to_commit: str) -> Dict[str, Any]:
        """Compare differences between two commits."""
        valid, error = validate_commit_hash(from_commit)
        if not valid:
            return {'error': error.replace('commit_hash', 'from_commit')}
        valid, error = validate_commit_hash(to_commit)
        if not valid:
            return {'error': error.replace('commit_hash', 'to_commit')}
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{sanitize_url_path(repo_slug)}/diff/{from_commit}..{to_commit}"
            response = self.session.get(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout)
            response.raise_for_status()
            return {'diff': response.text}
        except Exception as e:
            return {'error': str(e)}
    
    async def search(self, query: str) -> Dict[str, Any]:
        """Search using query."""
        try:
            logger.info(f"Searching Bitbucket: {query}")
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}"
            
            response = self.session.get(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout)
            
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
            
            response = self.session.get(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout, params={'pagelen': DEFAULT_PAGE_SIZE})
            response.raise_for_status()
            
            repos = response.json().get('values', [])
            return json.dumps(repos, indent=2)
        except Exception as e:
            return f"Error fetching repositories: {str(e)}"
    
    async def _get_pull_requests(self, repo: str) -> str:
        try:
            url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{repo}/pullrequests"
            
            response = self.session.get(url, auth=(self.auth.username, self.bitbucket_token), timeout=self.timeout, params={'pagelen': DEFAULT_PAGE_SIZE})
            response.raise_for_status()
            
            prs = response.json().get('values', [])
            return json.dumps(prs, indent=2)
        except Exception as e:
            return f"Error fetching pull requests: {str(e)}"
