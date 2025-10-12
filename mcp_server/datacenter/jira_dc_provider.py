import requests
import json
import os
from ..common.auth import DataCenterAuth

class JiraDataCenterProvider:
    def __init__(self):
        self.auth = DataCenterAuth()
        self.base_url = self.auth.get_base_url()
    
    async def search(self, jql: str) -> dict:
        try:
            url = f"{self.base_url}/rest/api/2/search"
            response = requests.get(url, headers=self.auth.get_auth_headers(), params={'jql': jql})
            response.raise_for_status()
            data = response.json()
            return {'total': data.get('total', 0), 'results': data.get('issues', [])}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_issue(self, issue_key: str) -> dict:
        try:
            url = f"{self.base_url}/rest/api/2/issue/{issue_key}"
            response = requests.get(url, headers=self.auth.get_auth_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def create_issue(self, project_key: str, summary: str, description: str, issue_type: str = "Task") -> dict:
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
            response = requests.post(url, headers=self.auth.get_auth_headers(), json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def update_issue(self, issue_key: str, fields: dict) -> dict:
        try:
            url = f"{self.base_url}/rest/api/2/issue/{issue_key}"
            payload = {"fields": fields}
            response = requests.put(url, headers=self.auth.get_auth_headers(), json=payload)
            response.raise_for_status()
            return {'success': True, 'issue_key': issue_key}
        except Exception as e:
            return {'error': str(e)}
    
    async def add_comment(self, issue_key: str, comment: str) -> dict:
        try:
            url = f"{self.base_url}/rest/api/2/issue/{issue_key}/comment"
            payload = {"body": comment}
            response = requests.post(url, headers=self.auth.get_auth_headers(), json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_issue_comments(self, issue_key: str) -> dict:
        try:
            url = f"{self.base_url}/rest/api/2/issue/{issue_key}/comment"
            response = requests.get(url, headers=self.auth.get_auth_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def transition_issue(self, issue_key: str, transition_id: str) -> dict:
        try:
            url = f"{self.base_url}/rest/api/2/issue/{issue_key}/transitions"
            payload = {"transition": {"id": transition_id}}
            response = requests.post(url, headers=self.auth.get_auth_headers(), json=payload)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_issue_transitions(self, issue_key: str) -> dict:
        try:
            url = f"{self.base_url}/rest/api/2/issue/{issue_key}/transitions"
            response = requests.get(url, headers=self.auth.get_auth_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def assign_issue(self, issue_key: str, account_id: str) -> dict:
        try:
            url = f"{self.base_url}/rest/api/2/issue/{issue_key}/assignee"
            payload = {"accountId": account_id}
            response = requests.put(url, headers=self.auth.get_auth_headers(), json=payload)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def delete_issue(self, issue_key: str) -> dict:
        try:
            url = f"{self.base_url}/rest/api/2/issue/{issue_key}"
            response = requests.delete(url, headers=self.auth.get_auth_headers())
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def list_projects(self) -> dict:
        try:
            url = f"{self.base_url}/rest/api/2/project"
            response = requests.get(url, headers=self.auth.get_auth_headers())
            response.raise_for_status()
            return {'projects': response.json()}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_project(self, project_key: str) -> dict:
        try:
            url = f"{self.base_url}/rest/api/2/project/{project_key}"
            response = requests.get(url, headers=self.auth.get_auth_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_issue_attachments(self, issue_key: str) -> dict:
        try:
            url = f"{self.base_url}/rest/api/2/issue/{issue_key}?fields=attachment"
            response = requests.get(url, headers=self.auth.get_auth_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_issue_watchers(self, issue_key: str) -> dict:
        try:
            url = f"{self.base_url}/rest/api/2/issue/{issue_key}/watchers"
            response = requests.get(url, headers=self.auth.get_auth_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
