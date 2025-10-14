# Phase 5: Advanced Search & Content Operations

## Overview
Implement 4 new tools for advanced search and content operations.

## Tools to Implement

### Jira (1 tool)
1. **get_user_permissions** - Check user permissions

### Confluence (3 tools)
1. **restore_page_version** - Restore previous version
2. **search_by_author** - Find content by author
3. **search_by_label** - Find content by label

### Bitbucket (0 tools)
- None in this phase

## Implementation Steps

### 1. Add Methods to Providers
- [ ] Add 1 method to `jira_provider.py` (Cloud)
- [ ] Add 1 method to `jira_dc_provider.py` (Data Center)
- [ ] Add 3 methods to `confluence_provider.py` (Cloud)
- [ ] Add 3 methods to `confluence_dc_provider.py` (Data Center)

### 2. Update Tool Definitions
- [ ] Add 4 new tool definitions to `tools.py`

### 3. Update Router
- [ ] Add routing for 4 new tools in `router.py`

### 4. Update Documentation
- [ ] Update README.md features section

### 5. Add Unit Tests
- [ ] Add 2 tests to `test_jira_provider.py`
- [ ] Add 2 tests to `test_jira_dc_provider.py`
- [ ] Add 6 tests to `test_confluence_provider.py`
- [ ] Add 6 tests to `test_confluence_dc_provider.py`

### 6. Update Integration Tests
- [ ] Add sample calls to `test_all_tools.py` (Cloud)
- [ ] Add sample calls to `test_all_dc_tools.py` (Data Center)
- [ ] Update tool counts: 78 → 82 total

### 7. Run Tests
- [ ] Run all unit tests (should be 127 total)
- [ ] Run integration tests
- [ ] Verify all tests pass

### 8. Commit Changes
- [ ] Git commit with message: "Phase 5: Add 4 advanced search & content tools"
- [ ] Push to both remotes

## API Endpoints

### Jira Cloud
- GET `/rest/api/3/mypermissions?projectKey={key}` - User permissions

### Jira Data Center
- GET `/rest/api/2/mypermissions?projectKey={key}` - User permissions

### Confluence Cloud
- PUT `/rest/api/content/{id}` - Restore version (update with old content)
- GET `/rest/api/content/search?cql=creator={accountId}` - Search by author
- GET `/rest/api/content/search?cql=label={label}` - Search by label

### Confluence Data Center
- PUT `/rest/api/content/{id}` - Restore version
- GET `/rest/api/content/search?cql=creator={username}` - Search by author
- GET `/rest/api/content/search?cql=label={label}` - Search by label
