import requests
import os
import logging
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ..common.auth import DataCenterAuth
from ..common.validation import validate_repo_slug, validate_pr_id, validate_non_empty, validate_path, validate_branch_name, validate_commit_hash, sanitize_url_path

logger = logging.getLogger(__name__)

# Pagination constants
LIST_PAGE_SIZE = 50

class BitbucketDCProvider:
    def __init__(self) -> None:
        # Support separate Bitbucket token
        bitbucket_token = os.getenv('BITBUCKET_PAT_TOKEN')
        if bitbucket_token:
            os.environ['ATLASSIAN_PAT_TOKEN'] = bitbucket_token
        self.auth = DataCenterAuth(service='bitbucket')
        self.base_url = self.auth.get_base_url()
        self.project = os.getenv('BITBUCKET_PROJECT', 'PROJECT')
        self.session = self._create_session()
        self.timeout = 25
        logger.info(f"BitbucketDCProvider initialized with base_url: {self.base_url}, project: {self.project}")
    
    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET", "POST", "PUT", "DELETE"])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    async def get_repository(self, repo_slug: str) -> Dict[str, Any]:
        """Get detailed repository information."""
        valid, error = validate_repo_slug(repo_slug)
        if not valid:
            logger.warning(f"Invalid repo_slug: {repo_slug}")
            return {'error': error}
        try:
            logger.info(f"Fetching repository: {repo_slug}")
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{sanitize_url_path(repo_slug)}"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching repository {repo_slug}: {e}")
            return {'error': str(e)}
    
    async def list_repositories(self) -> Dict[str, Any]:
        """List all repositories in workspace."""
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos"
            response = self.session.get(url, headers=headers, params={'limit': LIST_PAGE_SIZE}, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def list_pull_requests(self, repo_slug: str, state: str = "OPEN") -> Dict[str, Any]:
        """List pull requests with optional state filter."""
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests"
            params = {'state': state, 'limit': LIST_PAGE_SIZE}
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
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
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
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
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests"
            payload = {
                "title": title,
                "fromRef": {"id": f"refs/heads/{source_branch}", "repository": {"slug": repo_slug, "project": {"key": self.project}}},
                "toRef": {"id": f"refs/heads/{dest_branch}", "repository": {"slug": repo_slug, "project": {"key": self.project}}},
                "description": description
            }
            response = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
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
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{sanitize_url_path(repo_slug)}/browse/{sanitize_url_path(file_path)}"
            params = {'at': branch}
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            lines = response.json().get('lines', [])
            content = '\n'.join([line.get('text', '') for line in lines])
            return {'content': content, 'path': file_path}
        except Exception as e:
            return {'error': str(e)}
    
    async def list_commits(self, repo_slug: str, branch: str = "main") -> Dict[str, Any]:
        """List commits in a branch."""
        valid, error = validate_branch_name(branch)
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{sanitize_url_path(repo_slug)}/commits"
            params = {'until': branch, 'limit': LIST_PAGE_SIZE}
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
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
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{sanitize_url_path(repo_slug)}/commits/{commit_hash}"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def list_branches(self, repo_slug: str) -> Dict[str, Any]:
        """List all branches in a repository."""
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/branches"
            response = self.session.get(url, headers=headers, params={'limit': LIST_PAGE_SIZE}, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_pull_request_diff(self, repo_slug: str, pr_id: int) -> Dict[str, Any]:
        """Get the full diff for a pull request."""
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}/diff"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return {'diff': response.text}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_pull_request_comments(self, repo_slug: str, pr_id: int) -> Dict[str, Any]:
        """Retrieve all comments on a pull request."""
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}/activities"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def add_pr_comment(self, repo_slug: str, pr_id: int, comment: str) -> Dict[str, Any]:
        """Add a comment to a pull request."""
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}/comments"
            payload = {"text": comment}
            response = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def approve_pull_request(self, repo_slug: str, pr_id: int) -> Dict[str, Any]:
        """Approve a pull request."""
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}/approve"
            response = self.session.post(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def merge_pull_request(self, repo_slug: str, pr_id: int) -> Dict[str, Any]:
        """Merge an approved pull request."""
        try:
            headers = self.auth.get_auth_headers()
            pr_url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}"
            pr_response = self.session.get(pr_url, headers=headers, timeout=self.timeout)
            pr_response.raise_for_status()
            version = pr_response.json().get('version')
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}/merge"
            payload = {"version": version}
            response = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
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
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{sanitize_url_path(repo_slug)}/commits/{commit_hash}/diff"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return {'diff': response.text}
        except Exception as e:
            return {'error': str(e)}
    
    async def list_tags(self, repo_slug: str) -> Dict[str, Any]:
        """List all tags in a repository."""
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/tags"
            response = self.session.get(url, headers=headers, params={'limit': LIST_PAGE_SIZE}, timeout=self.timeout)
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
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{sanitize_url_path(repo_slug)}/browse/{sanitize_url_path(path)}"
            params = {'at': branch}
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def update_pull_request(self, repo_slug: str, pr_id: int, title: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """Update pull request title or description."""
        try:
            headers = self.auth.get_auth_headers()
            pr_url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}"
            pr_response = self.session.get(pr_url, headers=headers, timeout=self.timeout)
            pr_response.raise_for_status()
            pr_data = pr_response.json()
            payload = {"version": pr_data.get('version')}
            if title:
                payload["title"] = title
            if description:
                payload["description"] = description
            response = self.session.put(pr_url, headers=headers, json=payload, timeout=self.timeout)
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
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{sanitize_url_path(repo_slug)}/compare/diff"
            params = {'from': from_commit, 'to': to_commit}
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return {'diff': response.text}
        except Exception as e:
            return {'error': str(e)}
    
    async def search(self, query: str) -> Dict[str, Any]:
        """Search using query."""
        try:
            logger.info(f"Searching Bitbucket: {query}")
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            repos = response.json().get('values', [])
            results = [{'type': 'repository', 'name': r.get('name'), 'slug': r.get('slug'), 'description': r.get('description')} 
                      for r in repos if query.lower() in r.get('name', '').lower()]
            return {'results': results}
        except Exception as e:
            return {'error': str(e)}
