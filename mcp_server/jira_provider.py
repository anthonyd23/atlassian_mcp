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
    
    async def search(self, jql: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/rest/api/2/search"
            
            payload = {
                'jql': jql,
                'maxResults': 25,
                'fields': ['summary', 'status', 'assignee', 'priority', 'created']
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 410:
                return {'error': 'Jira API not available on free tier', 'results': []}
            
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
            url = f"{self.auth.get_base_url()}/rest/api/2/search"
            
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
