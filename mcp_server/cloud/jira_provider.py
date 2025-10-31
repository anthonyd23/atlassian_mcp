import requests
import json
import logging
from typing import Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ..common.auth import CloudAuth
from ..common.validation import validate_issue_key, validate_project_key, validate_non_empty, sanitize_url_path

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 25

class JiraProvider:
    def __init__(self) -> None:
        self.auth = CloudAuth()
        self.available = self.auth.is_available()
        self.session = self._create_session() if self.available else None
        self.timeout = 25
        if self.available:
            logger.info("JiraProvider initialized")
        else:
            logger.warning("JiraProvider not available - missing credentials")
    
    def _check_available(self) -> Dict[str, Any]:
        if not self.available:
            return {'error': 'Jira Cloud not configured. Set: ATLASSIAN_BASE_URL, ATLASSIAN_USERNAME, ATLASSIAN_API_TOKEN'}
        return None
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic"""
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    async def get_resource(self, uri: str) -> str:
        if uri == "atlassian://jira/projects":
            return await self._get_projects()
        elif "/issues" in uri:
            project_key = uri.split("/")[-2]
            return await self._get_issues(project_key)
        else:
            raise ValueError(f"Unknown Jira resource: {uri}")
    
    async def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Get full details of a Jira issue."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_issue_key(issue_key)
        if not valid:
            logger.warning(f"Invalid issue_key: {issue_key}")
            return {'error': error}
        try:
            logger.info(f"Fetching issue: {issue_key}")
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{sanitize_url_path(issue_key)}"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching issue {issue_key}: {e}")
            return {'error': str(e)}
    
    async def create_issue(self, project_key: str, summary: str, description: str, issue_type: str = "Task", custom_fields: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new Jira issue with optional custom fields."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_project_key(project_key)
        if not valid:
            return {'error': error}
        valid, error = validate_non_empty(summary, "summary")
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue"
            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": summary,
                    "issuetype": {"name": issue_type}
                }
            }
            if description:
                payload["fields"]["description"] = description
            if custom_fields:
                payload["fields"].update(custom_fields)
            response = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Update fields on an existing issue."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_issue_key(issue_key)
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{sanitize_url_path(issue_key)}"
            payload = {"fields": fields}
            response = self.session.put(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return {'success': True, 'issue_key': issue_key}
        except Exception as e:
            return {'error': str(e)}
    
    async def add_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
        """Add a comment to an issue."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{sanitize_url_path(issue_key)}/comment"
            payload = {"body": comment}
            response = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_issue_comments(self, issue_key: str) -> Dict[str, Any]:
        """Retrieve all comments on an issue."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{sanitize_url_path(issue_key)}/comment"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def transition_issue(self, issue_key: str, transition_id: str) -> Dict[str, Any]:
        """Move issue to a different status."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{sanitize_url_path(issue_key)}/transitions"
            payload = {"transition": {"id": transition_id}}
            response = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_issue_transitions(self, issue_key: str) -> Dict[str, Any]:
        """Get available status transitions for an issue."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{sanitize_url_path(issue_key)}/transitions"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def assign_issue(self, issue_key: str, account_id: str) -> Dict[str, Any]:
        """Assign an issue to a user."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{sanitize_url_path(issue_key)}/assignee"
            payload = {"accountId": account_id}
            response = self.session.put(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def delete_issue(self, issue_key: str) -> Dict[str, Any]:
        """Permanently delete an issue."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{sanitize_url_path(issue_key)}"
            response = self.session.delete(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def list_projects(self) -> Dict[str, Any]:
        """List all accessible Jira projects."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/project"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return {'projects': response.json()}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_project(self, project_key: str) -> Dict[str, Any]:
        """Get detailed information about a project."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_project_key(project_key)
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/project/{sanitize_url_path(project_key)}"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_issue_attachments(self, issue_key: str) -> Dict[str, Any]:
        """List all attachments on an issue."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{sanitize_url_path(issue_key)}?fields=attachment"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_issue_watchers(self, issue_key: str) -> Dict[str, Any]:
        """Get list of users watching an issue."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{sanitize_url_path(issue_key)}/watchers"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_user(self, account_id: str) -> Dict[str, Any]:
        """Get user details by account ID."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_non_empty(account_id, "account_id")
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/3/user?accountId={sanitize_url_path(account_id)}"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def search_users(self, query: str) -> Dict[str, Any]:
        """Search for users by name or email."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_non_empty(query, "query")
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/3/user/search?query={sanitize_url_path(query)}"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return {'users': response.json()}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_current_user(self) -> Dict[str, Any]:
        """Get authenticated user information."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/3/myself"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def link_issues(self, inward_issue: str, outward_issue: str, link_type: str = "Relates") -> Dict[str, Any]:
        """Create a link between two issues."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_issue_key(inward_issue)
        if not valid:
            return {'error': error.replace('issue_key', 'inward_issue')}
        valid, error = validate_issue_key(outward_issue)
        if not valid:
            return {'error': error.replace('issue_key', 'outward_issue')}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issueLink"
            payload = {
                "type": {"name": link_type},
                "inwardIssue": {"key": inward_issue},
                "outwardIssue": {"key": outward_issue}
            }
            response = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def add_worklog(self, issue_key: str, time_spent: str, comment: str = "") -> Dict[str, Any]:
        """Log time spent on an issue."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_issue_key(issue_key)
        if not valid:
            return {'error': error}
        valid, error = validate_non_empty(time_spent, "time_spent")
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{sanitize_url_path(issue_key)}/worklog"
            payload = {"timeSpent": time_spent}
            if comment:
                payload["comment"] = comment
            response = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_worklogs(self, issue_key: str) -> Dict[str, Any]:
        """Get time tracking data for an issue."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_issue_key(issue_key)
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{sanitize_url_path(issue_key)}/worklog"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def add_label(self, issue_key: str, label: str) -> Dict[str, Any]:
        """Add a label to an issue."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_issue_key(issue_key)
        if not valid:
            return {'error': error}
        valid, error = validate_non_empty(label, "label")
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{sanitize_url_path(issue_key)}"
            payload = {"update": {"labels": [{"add": label}]}}
            response = self.session.put(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def search_by_assignee(self, assignee: str, project_key: str = "") -> Dict[str, Any]:
        """Find issues assigned to a specific user."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_non_empty(assignee, "assignee")
        if not valid:
            return {'error': error}
        try:
            # Don't quote JQL functions like currentUser()
            if assignee.endswith('()'):
                jql = f"assignee = {assignee}"
            else:
                jql = f"assignee = '{assignee}'"
            if project_key:
                jql += f" AND project = '{project_key}'"
            return await self.search(jql)
        except Exception as e:
            return {'error': str(e)}
    
    async def search_by_reporter(self, reporter: str, project_key: str = "") -> Dict[str, Any]:
        """Find issues reported by a specific user."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_non_empty(reporter, "reporter")
        if not valid:
            return {'error': error}
        try:
            jql = f"reporter = '{reporter}'"
            if project_key:
                jql += f" AND project = '{project_key}'"
            return await self.search(jql)
        except Exception as e:
            return {'error': str(e)}
    
    async def get_recent_issues(self, days: int = 7, project_key: str = "") -> Dict[str, Any]:
        """Get recently updated issues."""
        check = self._check_available()
        if check:
            return check
        try:
            jql = f"updated >= -{days}d ORDER BY updated DESC"
            if project_key:
                jql = f"project = '{project_key}' AND " + jql
            return await self.search(jql)
        except Exception as e:
            return {'error': str(e)}
    
    async def set_priority(self, issue_key: str, priority: str) -> Dict[str, Any]:
        """Change issue priority."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_issue_key(issue_key)
        if not valid:
            return {'error': error}
        valid, error = validate_non_empty(priority, "priority")
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{sanitize_url_path(issue_key)}"
            payload = {"fields": {"priority": {"name": priority}}}
            response = self.session.put(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def list_boards(self) -> Dict[str, Any]:
        """Get all Scrum/Kanban boards."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/agile/1.0/board"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_board_issues(self, board_id: int) -> Dict[str, Any]:
        """Get issues on a board."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/agile/1.0/board/{board_id}/issue"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def list_sprints(self, board_id: int) -> Dict[str, Any]:
        """Get sprints for a board."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/agile/1.0/board/{board_id}/sprint"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_sprint_issues(self, sprint_id: int) -> Dict[str, Any]:
        """Get issues in a sprint."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/agile/1.0/sprint/{sprint_id}/issue"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_user_permissions(self, project_key: str = "") -> Dict[str, Any]:
        """Check user permissions."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/mypermissions"
            params = {'permissions': 'BROWSE_PROJECTS,CREATE_ISSUES,EDIT_ISSUES'}
            if project_key:
                params['projectKey'] = project_key
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def add_attachment(self, issue_key: str, filename: str, content: bytes) -> Dict[str, Any]:
        """Upload file to issue."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_issue_key(issue_key)
        if not valid:
            return {'error': error}
        valid, error = validate_non_empty(filename, "filename")
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            headers.pop('Content-Type', None)  # Let requests set multipart boundary
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{sanitize_url_path(issue_key)}/attachments"
            headers['X-Atlassian-Token'] = 'no-check'
            files = {'file': (filename, content)}
            response = self.session.post(url, headers=headers, files=files, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def search(self, jql: str) -> Dict[str, Any]:
        """Search using JQL query via Jira API v3."""
        check = self._check_available()
        if check:
            return check
        try:
            logger.info(f"Searching Jira with JQL: {jql}")
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/3/search/jql"
            
            params = {
                'jql': jql,
                'maxResults': 50,
                'fields': 'summary'
            }
            
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            issues = data.get('issues', [])
            total = data.get('total', 0)
            results = [{'key': i.get('key'), 'summary': i.get('fields', {}).get('summary', '')} for i in issues]
            
            result = {'total': total, 'results': results}
            if total > len(results):
                result['message'] = f'Showing {len(results)} of {total} results. Results limited to prevent response size exceeding 100K character limit.'
            return result
        except Exception as e:
            return {'error': str(e)}
    
    async def _get_projects(self) -> str:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/project"
            
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            projects = response.json()
            return json.dumps(projects, indent=2)
        except Exception as e:
            return f"Error fetching projects: {str(e)}"
    
    async def _get_issues(self, project_key: str) -> str:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/3/search"
            
            params = {
                'jql': f'project = {project_key}',
                'maxResults': DEFAULT_PAGE_SIZE
            }
            
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            issues = response.json().get('issues', [])
            return json.dumps(issues, indent=2)
        except Exception as e:
            return f"Error fetching issues: {str(e)}"
