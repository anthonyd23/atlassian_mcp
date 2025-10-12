import os
import base64

class BaseAuth:
    """Base authentication class"""
    def __init__(self):
        self.base_url = os.getenv('ATLASSIAN_BASE_URL')
    
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
    
    def get_auth_headers(self) -> dict:
        if not self.api_token or not self.username:
            raise ValueError("Missing Atlassian Cloud credentials (ATLASSIAN_API_TOKEN, ATLASSIAN_USERNAME)")
        
        credentials = f"{self.username}:{self.api_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        return {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        }

class DataCenterAuth(BaseAuth):
    """Authentication for Atlassian Data Center (Personal Access Token)"""
    def __init__(self):
        super().__init__()
        self.pat_token = os.getenv('ATLASSIAN_PAT_TOKEN')
    
    def get_auth_headers(self) -> dict:
        if not self.pat_token:
            raise ValueError("Missing Atlassian Data Center credentials (ATLASSIAN_PAT_TOKEN)")
        
        return {
            'Authorization': f'Bearer {self.pat_token}',
            'Content-Type': 'application/json'
        }

# Legacy Auth class for backward compatibility
Auth = CloudAuth
