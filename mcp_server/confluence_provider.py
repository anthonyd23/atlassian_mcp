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
    
    async def get_page(self, page_id: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/content/{page_id}?expand=body.storage,version"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_page_by_title(self, space_key: str, title: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/content"
            params = {'spaceKey': space_key, 'title': title, 'expand': 'body.storage,version'}
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def create_page(self, space_key: str, title: str, content: str, parent_id: str = None) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/content"
            payload = {
                "type": "page",
                "title": title,
                "space": {"key": space_key},
                "body": {"storage": {"value": content, "representation": "storage"}}
            }
            if parent_id:
                payload["ancestors"] = [{"id": parent_id}]
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def update_page(self, page_id: str, title: str, content: str, version: int) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/content/{page_id}"
            payload = {
                "version": {"number": version + 1},
                "title": title,
                "type": "page",
                "body": {"storage": {"value": content, "representation": "storage"}}
            }
            response = requests.put(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def delete_page(self, page_id: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/content/{page_id}"
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def list_pages(self, space_key: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/content"
            params = {'spaceKey': space_key, 'type': 'page', 'limit': 50}
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_space(self, space_key: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/space/{space_key}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def list_spaces(self) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/space"
            response = requests.get(url, headers=headers, params={'limit': 50})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_page_comments(self, page_id: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/content/{page_id}/child/comment"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def add_page_comment(self, page_id: str, comment: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/content"
            payload = {
                "type": "comment",
                "container": {"id": page_id, "type": "page"},
                "body": {"storage": {"value": comment, "representation": "storage"}}
            }
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_page_attachments(self, page_id: str) -> dict:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/content/{page_id}/child/attachment"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
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
