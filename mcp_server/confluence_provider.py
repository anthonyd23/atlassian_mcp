import requests
import json
from .auth import Auth

class ConfluenceProvider:
    def __init__(self):
        self.auth = Auth()
    
    async def get_resource(self, uri: str) -> str:
        if uri == "atlassian://confluence/spaces":
            return await self._get_spaces()
        elif "/pages" in uri:
            space_key = uri.split("/")[-2]
            return await self._get_pages(space_key)
        else:
            raise ValueError(f"Unknown Confluence resource: {uri}")
    
    async def search(self, query: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/search"
            
            params = {
                'cql': f'text ~ "{query}"',
                'limit': 25
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            results = response.json().get('results', [])
            formatted_results = []
            
            for result in results:
                formatted_results.append({
                    'type': result.get('content', {}).get('type'),
                    'title': result.get('content', {}).get('title'),
                    'space': result.get('content', {}).get('space', {}).get('name'),
                    'url': result.get('url')
                })
            
            return {'results': formatted_results}
        except Exception as e:
            return {'error': str(e)}
    
    async def _get_spaces(self) -> str:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/space"
            
            response = requests.get(url, headers=headers, params={'limit': 25})
            response.raise_for_status()
            
            spaces = response.json().get('results', [])
            return json.dumps(spaces, indent=2)
        except Exception as e:
            return f"Error fetching spaces: {str(e)}"
    
    async def _get_pages(self, space_key: str) -> str:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/space/{space_key}/content"
            
            response = requests.get(url, headers=headers, params={'limit': 25})
            response.raise_for_status()
            
            pages = response.json().get('results', [])
            return json.dumps(pages, indent=2)
        except Exception as e:
            return f"Error fetching pages: {str(e)}"
