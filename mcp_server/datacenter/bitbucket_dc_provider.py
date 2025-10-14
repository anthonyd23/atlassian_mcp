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
        self.auth = DataCenterAuth(service='bitbucket')
        self.available = self.auth.is_available()
        self.base_url = self.auth.get_base_url() if self.available else None
        self.project = os.getenv('BITBUCKET_PROJECT', 'PROJECT')
        self.session = self._create_session() if self.available else None
        self.timeout = 25
        if self.available:
            logger.info(f"BitbucketDCProvider initialized with base_url: {self.base_url}, project: {self.project}")
        else:
            logger.warning("BitbucketDCProvider not available - missing credentials")
    
    def _check_available(self) -> Dict[str, Any]:
        if not self.available:
            return {'error': 'Bitbucket Data Center not configured. Set: BITBUCKET_BASE_URL and BITBUCKET_PAT_TOKEN'}
        return None
    
    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET", "POST", "PUT", "DELETE"])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    async def get_repository(self, repo_slug: str) -> Dict[str, Any]:
        """Get detailed repository information."""
        check = self._check_available()
        if check:
            return check
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
        check = self._check_available()
        if check:
            return check
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
        check = self._check_available()
        if check:
            return check
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
        check = self._check_available()
        if check:
            return check
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
        check = self._check_available()
        if check:
            return check
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
        check = self._check_available()
        if check:
            return check
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
        check = self._check_available()
        if check:
            return check
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
        check = self._check_available()
        if check:
            return check
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
        check = self._check_available()
        if check:
            return check
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
        check = self._check_available()
        if check:
            return check
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
        check = self._check_available()
        if check:
            return check
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
        check = self._check_available()
        if check:
            return check
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
        check = self._check_available()
        if check:
            return check
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
        check = self._check_available()
        if check:
            return check
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
        check = self._check_available()
        if check:
            return check
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
        check = self._check_available()
        if check:
            return check
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
        check = self._check_available()
        if check:
            return check
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
        check = self._check_available()
        if check:
            return check
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
        check = self._check_available()
        if check:
            return check
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
    
    async def add_pr_reviewer(self, repo_slug: str, pr_id: int, account_id: str) -> Dict[str, Any]:
        """Add a reviewer to a pull request."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_pr_id(pr_id)
        if not valid:
            return {'error': error}
        valid, error = validate_non_empty(account_id, "account_id")
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}/participants"
            payload = {"user": {"name": account_id}, "role": "REVIEWER"}
            response = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def decline_pull_request(self, repo_slug: str, pr_id: int) -> Dict[str, Any]:
        """Decline a pull request."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_pr_id(pr_id)
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            pr_url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}"
            pr_response = self.session.get(pr_url, headers=headers, timeout=self.timeout)
            pr_response.raise_for_status()
            version = pr_response.json().get('version')
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}/decline"
            payload = {"version": version}
            response = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def create_branch(self, repo_slug: str, branch_name: str, from_branch: str = "main") -> Dict[str, Any]:
        """Create a new branch from an existing branch."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_branch_name(branch_name, "branch_name")
        if not valid:
            return {'error': error}
        valid, error = validate_branch_name(from_branch, "from_branch")
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/branches"
            payload = {
                "name": branch_name,
                "startPoint": from_branch
            }
            response = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def delete_branch(self, repo_slug: str, branch_name: str) -> Dict[str, Any]:
        """Delete a branch from the repository."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_branch_name(branch_name)
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/branch-utils/1.0/projects/{self.project}/repos/{repo_slug}/branches"
            payload = {"name": f"refs/heads/{branch_name}"}
            response = self.session.delete(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_user(self, username: str) -> Dict[str, Any]:
        """Get user details."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_non_empty(username, "username")
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/users/{sanitize_url_path(username)}"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_pr_activity(self, repo_slug: str, pr_id: int) -> Dict[str, Any]:
        """Get PR activity/timeline."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_pr_id(pr_id)
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}/activities"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_default_reviewers(self, repo_slug: str) -> Dict[str, Any]:
        """Get default reviewers for repository."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_repo_slug(repo_slug)
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/default-reviewers/1.0/projects/{self.project}/repos/{repo_slug}/reviewers"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def list_pull_requests_by_author(self, repo_slug: str, author: str) -> Dict[str, Any]:
        """Get PRs by specific user."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_non_empty(author, "author")
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests"
            params = {'filterText': f'author:{author}', 'limit': LIST_PAGE_SIZE}
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def list_commits_by_author(self, repo_slug: str, author: str, branch: str = "main") -> Dict[str, Any]:
        """Get commits by specific user."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_non_empty(author, "author")
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/commits"
            params = {'until': branch, 'author': author, 'limit': LIST_PAGE_SIZE}
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def request_changes(self, repo_slug: str, pr_id: int, comment: str = "") -> Dict[str, Any]:
        """Request changes on PR."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_pr_id(pr_id)
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}/participants"
            payload = {"status": "NEEDS_WORK"}
            response = self.session.put(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            if comment:
                comment_url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/pull-requests/{pr_id}/comments"
                self.session.post(comment_url, headers=headers, json={"text": comment}, timeout=self.timeout)
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_branch_restrictions(self, repo_slug: str) -> Dict[str, Any]:
        """Get branch permissions."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/branch-permissions/2.0/projects/{self.project}/repos/{repo_slug}/restrictions"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_build_status(self, repo_slug: str, commit_hash: str) -> Dict[str, Any]:
        """Get CI/CD build status."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_commit_hash(commit_hash)
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/rest/build-status/1.0/commits/{commit_hash}"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def create_webhook(self, repo_slug: str, url: str, events: list) -> Dict[str, Any]:
        """Set up webhooks."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_non_empty(url, "url")
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            api_url = f"{self.base_url}/rest/api/1.0/projects/{self.project}/repos/{repo_slug}/webhooks"
            payload = {
                "name": "MCP Webhook",
                "url": url,
                "active": True,
                "events": events if events else ["repo:refs_changed", "pr:opened"]
            }
            response = self.session.post(api_url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def search(self, query: str) -> Dict[str, Any]:
        """Search using query."""
        check = self._check_available()
        if check:
            return check
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
