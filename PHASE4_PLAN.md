# Phase 4: Agile & Content Management Tools

## Overview
Implement 6 new tools focused on Jira Agile boards/sprints and Confluence content management.

## Tools to Implement

### Jira (4 tools)
1. **list_boards** - Get Scrum/Kanban boards
2. **get_board_issues** - Get issues on a board
3. **list_sprints** - Get sprints for a board
4. **get_sprint_issues** - Get issues in a sprint

### Confluence (2 tools)
1. **get_user_content** - Get pages created by user
2. **get_recent_content** - Get recently updated content

## Implementation Steps

### 1. Add Methods to Providers
- [ ] Add 4 methods to `jira_provider.py` (Cloud)
- [ ] Add 4 methods to `jira_dc_provider.py` (Data Center)
- [ ] Add 2 methods to `confluence_provider.py` (Cloud)
- [ ] Add 2 methods to `confluence_dc_provider.py` (Data Center)

### 2. Update Tool Definitions
- [ ] Add 6 new tool definitions to `tools.py`

### 3. Update Router
- [ ] Add routing for 6 new tools in `router.py`

### 4. Update Documentation
- [ ] Update README.md features section

### 5. Add Unit Tests
- [ ] Add 6 tests to `test_jira_provider.py`
- [ ] Add 6 tests to `test_jira_dc_provider.py`
- [ ] Add 2 tests to `test_confluence_provider.py`
- [ ] Add 2 tests to `test_confluence_dc_provider.py`

### 6. Update Integration Tests
- [ ] Add sample calls to `test_all_tools.py` (Cloud)
- [ ] Add sample calls to `test_all_dc_tools.py` (Data Center)
- [ ] Update tool counts: 72 → 78 total

### 7. Run Tests
- [ ] Run all unit tests (should be 111 total)
- [ ] Run integration tests
- [ ] Verify all tests pass

### 8. Commit Changes
- [ ] Git commit with message: "Phase 4: Add 6 agile & content tools (Jira boards/sprints, Confluence content)"
- [ ] Push to both remotes

## API Endpoints

### Jira Cloud
- GET `/rest/agile/1.0/board` - List boards
- GET `/rest/agile/1.0/board/{boardId}/issue` - Board issues
- GET `/rest/agile/1.0/board/{boardId}/sprint` - List sprints
- GET `/rest/agile/1.0/sprint/{sprintId}/issue` - Sprint issues

### Jira Data Center
- Same as Cloud (Agile API available in DC)

### Confluence Cloud
- GET `/rest/api/content?creator={accountId}` - User content
- GET `/rest/api/content?orderby=lastmodified` - Recent content

### Confluence Data Center
- GET `/rest/api/content?creator={username}` - User content
- GET `/rest/api/content?orderby=lastmodified` - Recent content
