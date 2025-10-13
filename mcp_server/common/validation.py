"""Input validation for MCP tools"""
import re
from typing import Tuple, Any
from urllib.parse import quote

def validate_issue_key(issue_key: str) -> Tuple[bool, str]:
    """Validate Jira issue key format (e.g., PROJ-123)"""
    if not issue_key or not issue_key.strip():
        return False, "issue_key is required"
    if not re.match(r'^[A-Z][A-Z0-9]+-\d+$', issue_key):
        return False, "Invalid issue_key format. Expected: PROJECT-123"
    return True, ""

def validate_project_key(project_key: str) -> Tuple[bool, str]:
    """Validate Jira project key format"""
    if not project_key or not project_key.strip():
        return False, "project_key is required"
    if not re.match(r'^[A-Z][A-Z0-9]+$', project_key):
        return False, "Invalid project_key format. Expected: PROJ"
    return True, ""

def validate_page_id(page_id: str) -> Tuple[bool, str]:
    """Validate Confluence page ID"""
    if not page_id or not page_id.strip():
        return False, "page_id is required"
    if not page_id.isdigit():
        return False, "page_id must be numeric. Example: 12345"
    return True, ""

def validate_space_key(space_key: str) -> Tuple[bool, str]:
    """Validate Confluence space key"""
    if not space_key or not space_key.strip():
        return False, "space_key is required"
    if not re.match(r'^[A-Z0-9]+$', space_key):
        return False, "Invalid space_key format. Expected uppercase alphanumeric: SPACE or TEAM123"
    return True, ""

def validate_repo_slug(repo_slug: str) -> Tuple[bool, str]:
    """Validate repository slug"""
    if not repo_slug or not repo_slug.strip():
        return False, "repo_slug is required"
    if not re.match(r'^[a-z0-9_-]+$', repo_slug):
        return False, "Invalid repo_slug format. Expected lowercase with hyphens/underscores: my-repo or my_repo"
    return True, ""

def validate_pr_id(pr_id: Any) -> Tuple[bool, str]:
    """Validate pull request ID"""
    if pr_id is None:
        return False, "pr_id is required"
    if not isinstance(pr_id, int) or pr_id <= 0:
        return False, "pr_id must be a positive integer"
    return True, ""

def validate_non_empty(value: str, field_name: str) -> Tuple[bool, str]:
    """Validate non-empty string"""
    if not value or not value.strip():
        return False, f"{field_name} is required"
    return True, ""

def validate_path(path: str, field_name: str) -> Tuple[bool, str]:
    """Validate file/directory path"""
    if path is None:
        return True, ""  # Optional parameter
    if ".." in path:
        return False, f"{field_name} cannot contain path traversal (..)"
    return True, ""

def validate_branch_name(branch: str, field_name: str = "branch") -> Tuple[bool, str]:
    """Validate branch/tag name"""
    if not branch or not branch.strip():
        return False, f"{field_name} is required"
    if not re.match(r'^[a-zA-Z0-9/_.-]+$', branch):
        return False, f"{field_name} contains invalid characters. Use alphanumeric, /, _, ., -"
    return True, ""

def validate_commit_hash(commit_hash: str) -> Tuple[bool, str]:
    """Validate commit hash"""
    if not commit_hash or not commit_hash.strip():
        return False, "commit_hash is required"
    if not re.match(r'^[a-f0-9]{7,40}$', commit_hash):
        return False, "commit_hash must be 7-40 hexadecimal characters"
    return True, ""

def sanitize_url_path(value: str) -> str:
    """URL encode path component"""
    return quote(value, safe='')
