import requests
import json
import logging
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ..common.auth import Auth
from ..common.validation import sanitize_url_path,  validate_page_id, validate_space_key, validate_non_empty

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 25
LIST_PAGE_SIZE = 50

class ConfluenceProvider:
    def __init__(self) -> None:
        self.auth = Auth()
        self.available = self.auth.is_available()
        self.session = self._create_session() if self.available else None
        self.timeout = 25
        if self.available:
            logger.info("ConfluenceProvider initialized")
        else:
            logger.warning("ConfluenceProvider not available - missing credentials")
    
    def _check_available(self) -> Dict[str, Any]:
        if not self.available:
            return {'error': 'Confluence Cloud not configured. Set: ATLASSIAN_BASE_URL, ATLASSIAN_USERNAME, ATLASSIAN_API_TOKEN'}
        return None
    
    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET", "POST", "PUT", "DELETE"])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    async def get_resource(self, uri: str) -> str:
        if uri == "atlassian://confluence/spaces":
            return await self._get_spaces()
        elif "/pages" in uri:
            space_key = uri.split("/")[-2]
            return await self._get_pages(space_key)
        else:
            raise ValueError(f"Unknown Confluence resource: {uri}")
    
    async def get_page(self, page_id: str) -> Dict[str, Any]:
        """Get Confluence page content and metadata."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_page_id(page_id)
        if not valid:
            logger.warning(f"Invalid page_id: {page_id}")
            return {'error': error}
        try:
            logger.info(f"Fetching page: {page_id}")
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/content/{sanitize_url_path(page_id)}?expand=body.storage,version"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching page {page_id}: {e}")
            return {'error': str(e)}
    
    async def get_page_by_title(self, space_key: str, title: str) -> Dict[str, Any]:
        """Find and retrieve a page by title and space."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/content"
            params = {'spaceKey': space_key, 'title': title, 'expand': 'body.storage,version'}
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def create_page(self, space_key: str, title: str, content: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new Confluence page."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_space_key(space_key)
        if not valid:
            return {'error': error}
        valid, error = validate_non_empty(title, "title")
        if not valid:
            return {'error': error}
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
            response = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def update_page(self, page_id: str, title: str, content: str, version: int) -> Dict[str, Any]:
        """Update page title and content."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/content/{sanitize_url_path(page_id)}"
            payload = {
                "version": {"number": version + 1},
                "title": title,
                "type": "page",
                "body": {"storage": {"value": content, "representation": "storage"}}
            }
            response = self.session.put(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def delete_page(self, page_id: str) -> Dict[str, Any]:
        """Permanently delete a page."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/content/{sanitize_url_path(page_id)}"
            response = self.session.delete(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def list_pages(self, space_key: str) -> Dict[str, Any]:
        """List all pages in a space."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/content"
            params = {'spaceKey': space_key, 'type': 'page', 'limit': LIST_PAGE_SIZE}
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_space(self, space_key: str) -> Dict[str, Any]:
        """Get detailed information about a space."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_space_key(space_key)
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/space/{sanitize_url_path(space_key)}"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def list_spaces(self) -> Dict[str, Any]:
        """List all accessible Confluence spaces."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/space"
            response = self.session.get(url, headers=headers, params={'limit': LIST_PAGE_SIZE}, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_page_comments(self, page_id: str) -> Dict[str, Any]:
        """Retrieve all comments on a page."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/content/{sanitize_url_path(page_id)}/child/comment"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def add_page_comment(self, page_id: str, comment: str) -> Dict[str, Any]:
        """Add a comment to a page."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/content"
            payload = {
                "type": "comment",
                "container": {"id": page_id, "type": "page"},
                "body": {"storage": {"value": comment, "representation": "storage"}}
            }
            response = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_page_attachments(self, page_id: str) -> Dict[str, Any]:
        """List all files attached to a page."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/content/{sanitize_url_path(page_id)}/child/attachment"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def search(self, query: str) -> Dict[str, Any]:
        """Search using query."""
        check = self._check_available()
        if check:
            return check
        try:
            logger.info(f"Searching Confluence: {query}")
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/search"
            
            params = {
                'cql': f'text ~ "{query}"',
                'limit': DEFAULT_PAGE_SIZE
            }
            
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
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
            
            response = self.session.get(url, headers=headers, params={'limit': DEFAULT_PAGE_SIZE}, timeout=self.timeout)
            response.raise_for_status()
            
            spaces = response.json().get('results', [])
            return json.dumps(spaces, indent=2)
        except Exception as e:
            return f"Error fetching spaces: {str(e)}"
    
    async def _get_pages(self, space_key: str) -> str:
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.auth.get_base_url()}/wiki/rest/api/space/{sanitize_url_path(space_key)}/content"
            
            response = self.session.get(url, headers=headers, params={'limit': DEFAULT_PAGE_SIZE}, timeout=self.timeout)
            response.raise_for_status()
            
            pages = response.json().get('results', [])
            return json.dumps(pages, indent=2)
        except Exception as e:
            return f"Error fetching pages: {str(e)}"
