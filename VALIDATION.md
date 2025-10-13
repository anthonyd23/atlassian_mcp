# Input Validation

All MCP tools validate inputs before making API calls to provide clear error messages and prevent invalid requests.

## Validation Rules

### Jira

**Issue Key** (e.g., `PROJ-123`):
- Required
- Format: `[A-Z][A-Z0-9]+-\d+`
- Example: `MYPROJECT-456`

**Project Key** (e.g., `PROJ`):
- Required
- Format: `[A-Z][A-Z0-9]+`
- Example: `MYPROJ`

**Summary/Description**:
- Required (non-empty)

### Confluence

**Page ID**:
- Required
- Must be numeric
- Example: `12345678`

**Space Key** (e.g., `DOCS`):
- Required
- Format: `[A-Z0-9]+`
- Example: `TEAMDOCS`

**Title**:
- Required (non-empty)

### Bitbucket

**Repository Slug** (e.g., `my-repo`):
- Required
- Format: `[a-z0-9_-]+`
- Example: `my-awesome-repo`

**Pull Request ID**:
- Required
- Must be positive integer
- Example: `42`

**Branch Names**:
- Required (non-empty)
- Example: `feature/new-feature`

## Error Messages

When validation fails, tools return clear error messages:

```json
{
  "error": "issue_key is required"
}
```

```json
{
  "error": "Invalid issue_key format. Expected: PROJECT-123"
}
```

```json
{
  "error": "pr_id must be a positive integer"
}
```

## Example Usage

### Valid Request
```python
result = await jira.get_issue("PROJ-123")
# Returns: {"key": "PROJ-123", "fields": {...}}
```

### Invalid Request
```python
result = await jira.get_issue("")
# Returns: {"error": "issue_key is required"}

result = await jira.get_issue("invalid")
# Returns: {"error": "Invalid issue_key format. Expected: PROJECT-123"}
```

## Implementation

Validation is implemented in `mcp_server/common/validation.py`:

```python
def validate_issue_key(issue_key: str) -> tuple[bool, str]:
    """Validate Jira issue key format"""
    if not issue_key or not issue_key.strip():
        return False, "issue_key is required"
    if not re.match(r'^[A-Z][A-Z0-9]+-\d+$', issue_key):
        return False, "Invalid issue_key format. Expected: PROJECT-123"
    return True, ""
```

All provider methods check validation before making API calls:

```python
async def get_issue(self, issue_key: str) -> dict:
    valid, error = validate_issue_key(issue_key)
    if not valid:
        return {'error': error}
    # Proceed with API call
```

## Benefits

1. **Early Error Detection**: Catch invalid inputs before API calls
2. **Clear Error Messages**: Users know exactly what's wrong
3. **Reduced API Calls**: Don't waste API quota on invalid requests
4. **Consistent Validation**: Same rules across Cloud and Data Center
5. **Better UX**: Immediate feedback on input errors
