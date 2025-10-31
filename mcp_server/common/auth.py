import os
import base64
import requests
from typing import Optional, Tuple

class BaseAuth:
    """Base authentication class"""
    def __init__(self):
        self.base_url = os.getenv('ATLASSIAN_BASE_URL')
        self.available = False
    
    def is_available(self) -> bool:
        """Check if credentials are available"""
        return self.available
    
    def get_base_url(self) -> str:
        if not self.base_url:
            raise ValueError("Missing ATLASSIAN_BASE_URL")
        return self.base_url
    
    def get_auth_headers(self) -> dict:
        raise NotImplementedError("Subclasses must implement get_auth_headers")

class CloudAuth(BaseAuth):
    """Authentication for Atlassian Cloud (API Token)"""
    def __init__(self):
        super().__init__()
        self.api_token = os.getenv('ATLASSIAN_API_TOKEN')
        self.username = os.getenv('ATLASSIAN_USERNAME')
        self.available = bool(self.base_url and self.api_token and self.username)
    
    def get_auth_headers(self) -> dict:
        if not self.available:
            raise ValueError("Atlassian Cloud not configured. Set: ATLASSIAN_BASE_URL, ATLASSIAN_USERNAME, ATLASSIAN_API_TOKEN")
        
        credentials = f"{self.username}:{self.api_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        return {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        }

class DataCenterAuth(BaseAuth):
    """Authentication for Atlassian Data Center (Personal Access Token)"""
    def __init__(self, service: str):
        super().__init__()
        self.service = service
        self.pat_token = os.getenv(f'{service.upper()}_PAT_TOKEN')
        self.service_url = os.getenv(f'{service.upper()}_BASE_URL')
        self.available = bool(self.pat_token and self.service_url)
        self._username = None
    
    def get_base_url(self) -> str:
        if not self.service_url:
            raise ValueError(f"Missing {self.service.upper()}_BASE_URL")
        return self.service_url
    
    def get_auth_headers(self) -> dict:
        if not self.available:
            raise ValueError(f"{self.service.title()} Data Center not configured. Set: {self.service.upper()}_BASE_URL, {self.service.upper()}_PAT_TOKEN")
        
        return {
            'Authorization': f'Bearer {self.pat_token}',
            'Content-Type': 'application/json'
        }
    
    def get_current_username(self) -> Optional[str]:
        """Fetch current authenticated username from API (cached after first call)"""
        if self._username:
            return self._username
        if not self.available:
            return None
        try:
            headers = self.get_auth_headers()
            if self.service == 'bitbucket':
                # Bitbucket DC: No direct current user endpoint, must be provided by caller
                return None
            elif self.service == 'jira':
                url = f"{self.service_url}/rest/api/2/myself"
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                self._username = response.json().get('name')
            elif self.service == 'confluence':
                url = f"{self.service_url}/rest/api/user/current"
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                self._username = response.json().get('username')
            return self._username
        except Exception as e:
            pass
        return None
