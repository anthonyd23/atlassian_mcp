import requests
import os
import logging
from typing import Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ..common.auth import DataCenterAuth
from ..common.validation import sanitize_url_path,  validate_issue_key, validate_project_key, validate_non_empty

logger = logging.getLogger(__name__)

# Pagination constants
DEFAULT_PAGE_SIZE = 25

class JiraDCProvider:
    def __init__(self) -> None:
        # Support separate Jira token
        self.jira_token = os.getenv('JIRA_PAT_TOKEN') or os.getenv('ATLASSIAN_PAT_TOKEN')
        self.auth = DataCenterAuth(service='jira', token=self.jira_token)
        self.base_url = self.auth.get_base_url()
        self.session = self._create_session()
        self.timeout = 25
        logger.info(f"JiraDCProvider initialized with base_url: {self.base_url}")
    
    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET", "POST", "PUT", "DELETE"])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    async def search(self, jql: str) -> Dict[str, Any]:
        """Search using query."""
        valid, error = validate_non_empty(jql, "jql")
        if not valid:
            return {'error': error}
        try:
            logger.info(f"Searching Jira with JQL: {jql}")
            url = f"{self.base_url}/rest/api/2/search"
            response = self.session.get(url, headers=self.auth.get_auth_headers(), timeout=self.timeout, params={'jql': jql})
            response.raise_for_status()
            data = response.json()
            return {'total': data.get('total', 0), 'results': data.get('issues', [])}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Get full details of a Jira issue."""
        valid, error = validate_issue_key(issue_key)
        if not valid:
            logger.warning(f"Invalid issue_key: {issue_key}")
            return {'error': error}
        try:
            logger.info(f"Fetching issue: {issue_key}")
            url = f"{self.base_url}/rest/api/2/issue/{sanitize_url_path(issue_key)}"
            response = self.session.get(url, headers=self.auth.get_auth_headers(), timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching issue {issue_key}: {e}")
            return {'error': str(e)}
    
    async def create_issue(self, project_key: str, summary: str, description: str, issue_type: str = "Task") -> Dict[str, Any]:
        """Create a new Jira issue."""
        valid, error = validate_project_key(project_key)
        if not valid:
            return {'error': error}
        valid, error = validate_non_empty(summary, "summary")
        if not valid:
            return {'error': error}
        try:
            url = f"{self.base_url}/rest/api/2/issue"
            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": summary,
                    "description": description,
                    "issuetype": {"name": issue_type}
                }
            }
            response = self.session.post(url, headers=self.auth.get_auth_headers(), timeout=self.timeout, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Update fields on an existing issue."""
        valid, error = validate_issue_key(issue_key)
        if not valid:
            return {'error': error}
        try:
            url = f"{self.base_url}/rest/api/2/issue/{sanitize_url_path(issue_key)}"
            payload = {"fields": fields}
            response = self.session.put(url, headers=self.auth.get_auth_headers(), timeout=self.timeout, json=payload)
            response.raise_for_status()
            return {'success': True, 'issue_key': issue_key}
        except Exception as e:
            return {'error': str(e)}
    
    async def add_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
        """Add a comment to an issue."""
        try:
            url = f"{self.base_url}/rest/api/2/issue/{sanitize_url_path(issue_key)}/comment"
            payload = {"body": comment}
            response = self.session.post(url, headers=self.auth.get_auth_headers(), timeout=self.timeout, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_issue_comments(self, issue_key: str) -> Dict[str, Any]:
        """Retrieve all comments on an issue."""
        try:
            url = f"{self.base_url}/rest/api/2/issue/{sanitize_url_path(issue_key)}/comment"
            response = self.session.get(url, headers=self.auth.get_auth_headers(), timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def transition_issue(self, issue_key: str, transition_id: str) -> Dict[str, Any]:
        """Move issue to a different status."""
        try:
            url = f"{self.base_url}/rest/api/2/issue/{sanitize_url_path(issue_key)}/transitions"
            payload = {"transition": {"id": transition_id}}
            response = self.session.post(url, headers=self.auth.get_auth_headers(), timeout=self.timeout, json=payload)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_issue_transitions(self, issue_key: str) -> Dict[str, Any]:
        """Get available status transitions for an issue."""
        try:
            url = f"{self.base_url}/rest/api/2/issue/{sanitize_url_path(issue_key)}/transitions"
            response = self.session.get(url, headers=self.auth.get_auth_headers(), timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def assign_issue(self, issue_key: str, account_id: str) -> Dict[str, Any]:
        """Assign an issue to a user."""
        try:
            url = f"{self.base_url}/rest/api/2/issue/{sanitize_url_path(issue_key)}/assignee"
            payload = {"accountId": account_id}
            response = self.session.put(url, headers=self.auth.get_auth_headers(), timeout=self.timeout, json=payload)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def delete_issue(self, issue_key: str) -> Dict[str, Any]:
        """Permanently delete an issue."""
        try:
            url = f"{self.base_url}/rest/api/2/issue/{sanitize_url_path(issue_key)}"
            response = self.session.delete(url, headers=self.auth.get_auth_headers(), timeout=self.timeout)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def list_projects(self) -> Dict[str, Any]:
        """List all accessible Jira projects."""
        try:
            url = f"{self.base_url}/rest/api/2/project"
            response = self.session.get(url, headers=self.auth.get_auth_headers(), timeout=self.timeout)
            response.raise_for_status()
            return {'projects': response.json()}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_project(self, project_key: str) -> Dict[str, Any]:
        """Get detailed information about a project."""
        valid, error = validate_project_key(project_key)
        if not valid:
            return {'error': error}
        try:
            url = f"{self.base_url}/rest/api/2/project/{sanitize_url_path(project_key)}"
            response = self.session.get(url, headers=self.auth.get_auth_headers(), timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_issue_attachments(self, issue_key: str) -> Dict[str, Any]:
        """List all attachments on an issue."""
        try:
            url = f"{self.base_url}/rest/api/2/issue/{sanitize_url_path(issue_key)}?fields=attachment"
            response = self.session.get(url, headers=self.auth.get_auth_headers(), timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_issue_watchers(self, issue_key: str) -> Dict[str, Any]:
        """Get list of users watching an issue."""
        try:
            url = f"{self.base_url}/rest/api/2/issue/{sanitize_url_path(issue_key)}/watchers"
            response = self.session.get(url, headers=self.auth.get_auth_headers(), timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
