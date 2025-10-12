import requests
import json
from .auth import Auth

class JiraProvider:
    def __init__(self):
        self.auth = Auth()
    
    async def get_resource(self, uri: str) -> str:
        if uri == "atlassian://jira/projects":
            return await self._get_projects()
        elif "/issues" in uri:
            project_key = uri.split("/")[-2]
            return await self._get_issues(project_key)
        else:
            raise ValueError(f"Unknown Jira resource: {uri}")
    
    async def get_issue(self, issue_key: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{issue_key}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def create_issue(self, project_key: str, summary: str, description: str, issue_type: str = "Task") -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue"
            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": summary,
                    "description": description,
                    "issuetype": {"name": issue_type}
                }
            }
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def update_issue(self, issue_key: str, fields: dict) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{issue_key}"
            payload = {"fields": fields}
            response = requests.put(url, headers=headers, json=payload)
            response.raise_for_status()
            return {'success': True, 'issue_key': issue_key}
        except Exception as e:
            return {'error': str(e)}
    
    async def add_comment(self, issue_key: str, comment: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{issue_key}/comment"
            payload = {"body": comment}
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_issue_comments(self, issue_key: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{issue_key}/comment"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def transition_issue(self, issue_key: str, transition_id: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{issue_key}/transitions"
            payload = {"transition": {"id": transition_id}}
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_issue_transitions(self, issue_key: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{issue_key}/transitions"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def assign_issue(self, issue_key: str, account_id: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{issue_key}/assignee"
            payload = {"accountId": account_id}
            response = requests.put(url, headers=headers, json=payload)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def delete_issue(self, issue_key: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{issue_key}"
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def list_projects(self) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/project"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return {'projects': response.json()}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_project(self, project_key: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/project/{project_key}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_issue_attachments(self, issue_key: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{issue_key}?fields=attachment"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_issue_watchers(self, issue_key: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/issue/{issue_key}/watchers"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def search(self, jql: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/3/search/jql"
            
            payload = {
                'jql': jql,
                'maxResults': 25,
                'fields': ['summary', 'status', 'assignee', 'priority', 'created']
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            issues = data.get('issues', [])
            
            formatted_results = []
            for issue in issues:
                fields = issue.get('fields', {})
                formatted_results.append({
                    'key': issue.get('key'),
                    'summary': fields.get('summary'),
                    'status': fields.get('status', {}).get('name'),
                    'assignee': fields.get('assignee', {}).get('displayName') if fields.get('assignee') else None,
                    'priority': fields.get('priority', {}).get('name'),
                    'created': fields.get('created')
                })
            
            return {
                'total': data.get('total', 0),
                'results': formatted_results
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def _get_projects(self) -> str:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/project"
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            projects = response.json()
            return json.dumps(projects, indent=2)
        except Exception as e:
            return f"Error fetching projects: {str(e)}"
    
    async def _get_issues(self, project_key: str) -> str:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/3/search/jql"
            
            payload = {
                'jql': f'project = {project_key}',
                'maxResults': 25
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            issues = response.json().get('issues', [])
            return json.dumps(issues, indent=2)
        except Exception as e:
            return f"Error fetching issues: {str(e)}"
