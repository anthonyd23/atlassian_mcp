import requests
import json
import os
import logging
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ..common.auth import DataCenterAuth
from ..common.validation import sanitize_url_path,  validate_page_id, validate_space_key, validate_non_empty

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 25
LIST_PAGE_SIZE = 50

class ConfluenceDCProvider:
    def __init__(self) -> None:
        self.auth = DataCenterAuth(service='confluence')
        self.available = self.auth.is_available()
        self.base_url = self.auth.get_base_url() if self.available else None
        self.session = self._create_session() if self.available else None
        self.timeout = 25
        if self.available:
            logger.info(f"ConfluenceDCProvider initialized with base_url: {self.base_url}")
        else:
            logger.warning("ConfluenceDCProvider not available - missing credentials")
    
    def _check_available(self) -> Dict[str, Any]:
        if not self.available:
            return {'error': 'Confluence Data Center not configured. Set: CONFLUENCE_BASE_URL and CONFLUENCE_PAT_TOKEN'}
        return None
    
    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET", "POST", "PUT", "DELETE"])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
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
            url = f"{self.base_url}/wiki/rest/api/content/{sanitize_url_path(page_id)}?expand=body.storage,version"
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
            url = f"{self.base_url}/wiki/rest/api/content"
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
            url = f"{self.base_url}/wiki/rest/api/content"
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
            url = f"{self.base_url}/wiki/rest/api/content/{sanitize_url_path(page_id)}"
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
            url = f"{self.base_url}/wiki/rest/api/content/{sanitize_url_path(page_id)}"
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
            url = f"{self.base_url}/wiki/rest/api/content"
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
            url = f"{self.base_url}/wiki/rest/api/space/{sanitize_url_path(space_key)}"
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
            url = f"{self.base_url}/wiki/rest/api/space"
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
            url = f"{self.base_url}/wiki/rest/api/content/{sanitize_url_path(page_id)}/child/comment"
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
            url = f"{self.base_url}/wiki/rest/api/content"
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
            url = f"{self.base_url}/wiki/rest/api/content/{sanitize_url_path(page_id)}/child/attachment"
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
            url = f"{self.base_url}/wiki/rest/api/user?accountId={sanitize_url_path(account_id)}"
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
            url = f"{self.base_url}/wiki/rest/api/search/user?cql=user.fullname~\"{sanitize_url_path(query)}\""
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return {'users': response.json().get('results', [])}
        except Exception as e:
            return {'error': str(e)}
    
    async def add_label(self, page_id: str, label: str) -> Dict[str, Any]:
        """Add a label to a page."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_page_id(page_id)
        if not valid:
            return {'error': error}
        valid, error = validate_non_empty(label, "label")
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/wiki/rest/api/content/{sanitize_url_path(page_id)}/label"
            payload = {"prefix": "global", "name": label}
            response = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}
    
    async def get_labels(self, page_id: str) -> Dict[str, Any]:
        """Get all labels on a page."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_page_id(page_id)
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/wiki/rest/api/content/{sanitize_url_path(page_id)}/label"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_page_history(self, page_id: str) -> Dict[str, Any]:
        """Get page version history."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_page_id(page_id)
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/wiki/rest/api/content/{sanitize_url_path(page_id)}/history"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_page_restrictions(self, page_id: str) -> Dict[str, Any]:
        """View page permissions."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_page_id(page_id)
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/wiki/rest/api/content/{sanitize_url_path(page_id)}/restriction"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def set_page_restrictions(self, page_id: str, restrictions: Dict[str, Any]) -> Dict[str, Any]:
        """Update page permissions."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_page_id(page_id)
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/wiki/rest/api/content/{sanitize_url_path(page_id)}/restriction"
            response = self.session.put(url, headers=headers, json=restrictions, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def copy_page(self, page_id: str, new_title: str, space_key: str = "") -> Dict[str, Any]:
        """Duplicate a page."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_page_id(page_id)
        if not valid:
            return {'error': error}
        valid, error = validate_non_empty(new_title, "new_title")
        if not valid:
            return {'error': error}
        try:
            # Get original page
            page = await self.get_page(page_id)
            if 'error' in page:
                return page
            # Create copy
            target_space = space_key if space_key else page.get('space', {}).get('key')
            content = page.get('body', {}).get('storage', {}).get('value', '')
            return await self.create_page(target_space, new_title, content)
        except Exception as e:
            return {'error': str(e)}
    
    async def get_user_content(self, username: str) -> Dict[str, Any]:
        """Get pages created by a user."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_non_empty(username, "username")
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/wiki/rest/api/content/search"
            params = {'cql': f'creator = {username}', 'limit': DEFAULT_PAGE_SIZE}
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def get_recent_content(self, days: int = 7, space_key: str = "") -> Dict[str, Any]:
        """Get recently updated content."""
        check = self._check_available()
        if check:
            return check
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/wiki/rest/api/content"
            params = {'orderby': 'lastmodified', 'limit': DEFAULT_PAGE_SIZE}
            if space_key:
                params['spaceKey'] = space_key
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def restore_page_version(self, page_id: str, version: int) -> Dict[str, Any]:
        """Restore previous version."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_page_id(page_id)
        if not valid:
            return {'error': error}
        try:
            # Get the specific version
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/wiki/rest/api/content/{sanitize_url_path(page_id)}?version={version}&expand=body.storage"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            old_version = response.json()
            # Get current version
            current = await self.get_page(page_id)
            if 'error' in current:
                return current
            # Update with old content
            return await self.update_page(
                page_id,
                old_version.get('title'),
                old_version.get('body', {}).get('storage', {}).get('value', ''),
                current.get('version', {}).get('number', 1)
            )
        except Exception as e:
            return {'error': str(e)}
    
    async def search_by_author(self, username: str, space_key: str = "") -> Dict[str, Any]:
        """Find content by author."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_non_empty(username, "username")
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/wiki/rest/api/content/search"
            cql = f'creator = {username}'
            if space_key:
                cql += f' AND space = {space_key}'
            params = {'cql': cql, 'limit': DEFAULT_PAGE_SIZE}
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    async def search_by_label(self, label: str, space_key: str = "") -> Dict[str, Any]:
        """Find content by label."""
        check = self._check_available()
        if check:
            return check
        valid, error = validate_non_empty(label, "label")
        if not valid:
            return {'error': error}
        try:
            headers = self.auth.get_auth_headers()
            url = f"{self.base_url}/wiki/rest/api/content/search"
            cql = f'label = {label}'
            if space_key:
                cql += f' AND space = {space_key}'
            params = {'cql': cql, 'limit': DEFAULT_PAGE_SIZE}
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
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
            url = f"{self.base_url}/wiki/rest/api/search"
            params = {'cql': f'text ~ "{query}"', 'limit': DEFAULT_PAGE_SIZE}
            response = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            results = response.json().get('results', [])
            formatted_results = [{
                'type': r.get('content', {}).get('type'),
                'title': r.get('content', {}).get('title'),
                'space': r.get('content', {}).get('space', {}).get('name'),
                'url': r.get('url')
            } for r in results]
            return {'results': formatted_results}
        except Exception as e:
            return {'error': str(e)}
