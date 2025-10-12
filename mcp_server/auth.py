import os
from typing import Optional

class Auth:
    def __init__(self):
        self.api_token = os.getenv('ATLASSIAN_API_TOKEN')
        self.username = os.getenv('ATLASSIAN_USERNAME')
        self.base_url = os.getenv('ATLASSIAN_BASE_URL')
    
    def get_auth_headers(self) -> dict:
        if not self.api_token or not self.username:
            raise ValueError("Missing Atlassian credentials")
        
        import base64
        credentials = f"{self.username}:{self.api_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        return {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        }
    
    def get_base_url(self) -> str:
        if not self.base_url:
            raise ValueError("Missing ATLASSIAN_BASE_URL")
        return self.base_url
