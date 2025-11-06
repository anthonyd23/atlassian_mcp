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
    # Allow team spaces (TEAM, PROJ) or personal spaces (~accountId)
    if not re.match(r'^([A-Z0-9]+|~[a-zA-Z0-9:_-]+)$', space_key):
        return False, "Invalid space_key format. Expected: SPACE, TEAM123, or ~accountId"
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

def validate_account_id(account_id: str) -> Tuple[bool, str]:
    """Validate Jira/Confluence user account ID"""
    if not account_id or not account_id.strip():
        return False, "account_id is required"
    return True, ""

def validate_transition_id(transition_id: str) -> Tuple[bool, str]:
    """Validate Jira transition ID"""
    if not transition_id or not transition_id.strip():
        return False, "transition_id is required"
    if not transition_id.isdigit():
        return False, "transition_id must be numeric"
    return True, ""

def validate_board_id(board_id: Any) -> Tuple[bool, str]:
    """Validate Jira board ID"""
    if board_id is None:
        return False, "board_id is required"
    if not isinstance(board_id, int) or board_id <= 0:
        return False, "board_id must be a positive integer"
    return True, ""

def validate_sprint_id(sprint_id: Any) -> Tuple[bool, str]:
    """Validate Jira sprint ID"""
    if sprint_id is None:
        return False, "sprint_id is required"
    if not isinstance(sprint_id, int) or sprint_id <= 0:
        return False, "sprint_id must be a positive integer"
    return True, ""

def validate_version_number(version: Any) -> Tuple[bool, str]:
    """Validate Confluence page version number"""
    if version is None:
        return False, "version is required"
    if not isinstance(version, int) or version <= 0:
        return False, "version must be a positive integer"
    return True, ""

def validate_time_spent(time_spent: str) -> Tuple[bool, str]:
    """Validate Jira worklog time format (e.g., 2h, 1d 4h, 30m)"""
    if not time_spent or not time_spent.strip():
        return False, "time_spent is required"
    if not re.match(r'^(\d+[wdhm]\s*)+$', time_spent.strip()):
        return False, "Invalid time_spent format. Expected: 2h, 1d 4h, 30m, 1w 2d"
    return True, ""

def validate_priority(priority: str) -> Tuple[bool, str]:
    """Validate Jira priority name"""
    if not priority or not priority.strip():
        return False, "priority is required"
    return True, ""

def validate_label(label: str) -> Tuple[bool, str]:
    """Validate label format"""
    if not label or not label.strip():
        return False, "label is required"
    if not re.match(r'^[a-zA-Z0-9_-]+$', label):
        return False, "label can only contain alphanumeric characters, hyphens, and underscores"
    return True, ""

def validate_cql(cql: str) -> Tuple[bool, str]:
    """Validate CQL query"""
    if not cql or not cql.strip():
        return False, "cql is required"
    return True, ""

def validate_jql(jql: str) -> Tuple[bool, str]:
    """Validate JQL query"""
    if not jql or not jql.strip():
        return False, "jql is required"
    return True, ""

def validate_username(username: str) -> Tuple[bool, str]:
    """Validate username"""
    if not username or not username.strip():
        return False, "username is required"
    return True, ""

def validate_url(url: str) -> Tuple[bool, str]:
    """Validate URL format"""
    if not url or not url.strip():
        return False, "url is required"
    if not re.match(r'^https?://', url):
        return False, "url must start with http:// or https://"
    return True, ""

def validate_pr_state(state: str) -> Tuple[bool, str]:
    """Validate pull request state"""
    valid_states = ["OPEN", "MERGED", "DECLINED", "ALL"]
    if state.upper() not in valid_states:
        return False, f"state must be one of: {', '.join(valid_states)}"
    return True, ""

def validate_events_list(events: Any) -> Tuple[bool, str]:
    """Validate webhook events list"""
    if not events or not isinstance(events, list) or len(events) == 0:
        return False, "events must be a non-empty list"
    return True, ""

def sanitize_url_path(value: str) -> str:
    """URL encode path component"""
    return quote(value, safe='')
