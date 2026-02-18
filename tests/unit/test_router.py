import pytest
from unittest.mock import Mock, AsyncMock, patch
from mcp_server.common.router import route_tool_call


@pytest.fixture
def mock_providers():
    jira = Mock()
    # Mock all Jira methods
    for method in ['search', 'get_issue', 'create_issue', 'update_issue', 'add_comment', 
                   'get_issue_comments', 'transition_issue', 'get_issue_transitions', 'assign_issue',
                   'delete_issue', 'list_projects', 'get_project', 'get_issue_attachments',
                   'get_issue_watchers', 'get_user', 'search_users', 'get_current_user',
                   'link_issues', 'add_worklog', 'get_worklogs', 'add_label', 'search_by_assignee',
                   'search_by_reporter', 'get_recent_issues', 'set_priority', 'list_boards',
                   'get_board_issues', 'list_sprints', 'get_sprint_issues', 'get_user_permissions',
                   'add_attachment']:
        setattr(jira, method, AsyncMock(return_value={"success": True}))
    
    confluence = Mock()
    # Mock all Confluence methods
    for method in ['search', 'get_page', 'get_page_by_title', 'create_page', 'update_page',
                   'delete_page', 'list_pages', 'get_space', 'list_spaces', 'get_page_comments',
                   'add_page_comment', 'get_page_attachments', 'get_user', 'search_users',
                   'add_label', 'get_labels', 'get_page_history', 'get_page_restrictions',
                   'set_page_restrictions', 'copy_page', 'get_user_content', 'get_recent_content',
                   'restore_page_version', 'search_by_author', 'search_by_label', 'move_page',
                   'get_child_pages', 'get_descendants', 'get_ancestors', 'cql_search']:
        setattr(confluence, method, AsyncMock(return_value={"success": True}))
    
    bitbucket = Mock()
    # Mock all Bitbucket methods
    for method in ['search', 'get_repository', 'list_repositories', 'list_pull_requests',
                   'get_pull_request', 'create_pull_request', 'get_file_content', 'list_commits',
                   'get_commit', 'list_branches', 'get_pull_request_diff', 'get_pull_request_comments',
                   'add_pr_comment', 'approve_pull_request', 'merge_pull_request', 'get_commit_diff',
                   'list_tags', 'list_directory', 'update_pull_request', 'compare_commits',
                   'add_pr_reviewer', 'decline_pull_request', 'create_branch', 'delete_branch',
                   'get_user', 'get_pr_activity', 'get_default_reviewers', 'list_pull_requests_by_author',
                   'list_commits_by_author', 'request_changes', 'get_branch_restrictions',
                   'get_build_status', 'create_webhook']:
        setattr(bitbucket, method, AsyncMock(return_value={"success": True}))
    
    return jira, confluence, bitbucket


@pytest.mark.asyncio
async def test_route_jira_search(mock_providers):
    jira, confluence, bitbucket = mock_providers
    
    result = await route_tool_call("search_jira", {"jql": "project = TEST"}, jira, confluence, bitbucket)
    
    assert result == {"success": True}
    jira.search.assert_called_once_with("project = TEST")


@pytest.mark.asyncio
async def test_route_jira_get_issue(mock_providers):
    jira, confluence, bitbucket = mock_providers
    
    result = await route_tool_call("get_issue", {"issue_key": "TEST-123"}, jira, confluence, bitbucket)
    
    assert result == {"success": True}
    jira.get_issue.assert_called_once_with("TEST-123")


@pytest.mark.asyncio
async def test_route_confluence_search(mock_providers):
    jira, confluence, bitbucket = mock_providers
    
    result = await route_tool_call("search_confluence", {"query": "test"}, jira, confluence, bitbucket)
    
    assert result == {"success": True}
    confluence.search.assert_called_once_with("test")


@pytest.mark.asyncio
async def test_route_confluence_get_page(mock_providers):
    jira, confluence, bitbucket = mock_providers
    
    result = await route_tool_call("get_page", {"page_id": "123"}, jira, confluence, bitbucket)
    
    assert result == {"success": True}
    confluence.get_page.assert_called_once_with("123", 0, 80000)


@pytest.mark.asyncio
async def test_route_bitbucket_search(mock_providers):
    jira, confluence, bitbucket = mock_providers
    
    result = await route_tool_call("search_bitbucket", {"query": "test"}, jira, confluence, bitbucket)
    
    assert result == {"success": True}
    bitbucket.search.assert_called_once_with("test")


@pytest.mark.asyncio
async def test_route_bitbucket_get_repository(mock_providers):
    jira, confluence, bitbucket = mock_providers
    
    result = await route_tool_call("get_repository", {"repo_slug": "repo"}, jira, confluence, bitbucket)
    
    assert result == {"success": True}
    bitbucket.get_repository.assert_called_once_with("repo")


@pytest.mark.asyncio
async def test_route_unknown_tool(mock_providers):
    jira, confluence, bitbucket = mock_providers
    
    with pytest.raises(ValueError, match="Unknown tool"):
        await route_tool_call("unknown_tool", {}, jira, confluence, bitbucket)


# Jira tools (31 total)
@pytest.mark.asyncio
async def test_jira_tools(mock_providers):
    jira, confluence, bitbucket = mock_providers
    
    tools = [
        ("search_jira", {"jql": "test"}),
        ("get_issue", {"issue_key": "TEST-1"}),
        ("create_issue", {"project_key": "TEST", "summary": "test", "description": "test"}),
        ("update_issue", {"issue_key": "TEST-1", "fields": {}}),
        ("add_comment", {"issue_key": "TEST-1", "comment": "test"}),
        ("get_issue_comments", {"issue_key": "TEST-1"}),
        ("transition_issue", {"issue_key": "TEST-1", "transition_id": "1"}),
        ("get_issue_transitions", {"issue_key": "TEST-1"}),
        ("assign_issue", {"issue_key": "TEST-1", "account_id": "123"}),
        ("delete_issue", {"issue_key": "TEST-1"}),
        ("list_projects", {}),
        ("get_project", {"project_key": "TEST"}),
        ("get_issue_attachments", {"issue_key": "TEST-1"}),
        ("get_issue_watchers", {"issue_key": "TEST-1"}),
        ("get_user", {"account_id": "123"}),
        ("search_users", {"query": "test"}),
        ("get_current_user", {}),
        ("link_issues", {"inward_issue": "TEST-1", "outward_issue": "TEST-2"}),
        ("add_worklog", {"issue_key": "TEST-1", "time_spent": "2h"}),
        ("get_worklogs", {"issue_key": "TEST-1"}),
        ("add_label", {"issue_key": "TEST-1", "label": "test"}),
        ("search_by_assignee", {"assignee": "user"}),
        ("search_by_reporter", {"reporter": "user"}),
        ("get_recent_issues", {}),
        ("set_priority", {"issue_key": "TEST-1", "priority": "High"}),
        ("list_boards", {}),
        ("get_board_issues", {"board_id": 1}),
        ("list_sprints", {"board_id": 1}),
        ("get_sprint_issues", {"sprint_id": 1}),
        ("get_user_permissions", {}),
        ("add_attachment", {"issue_key": "TEST-1", "filename": "test.txt", "content": "test"}),
    ]
    
    for tool_name, args in tools:
        result = await route_tool_call(tool_name, args, jira, confluence, bitbucket)
        assert result == {"success": True}


# Confluence tools (30 total)
@pytest.mark.asyncio
async def test_confluence_tools(mock_providers):
    jira, confluence, bitbucket = mock_providers
    
    tools = [
        ("search_confluence", {"query": "test"}),
        ("get_page", {"page_id": "123"}),
        ("get_page_by_title", {"space_key": "TEST", "title": "test"}),
        ("create_page", {"space_key": "TEST", "title": "test", "content": "test"}),
        ("update_page", {"page_id": "123", "title": "test", "content": "test", "version": 1}),
        ("delete_page", {"page_id": "123"}),
        ("list_pages", {"space_key": "TEST"}),
        ("get_space", {"space_key": "TEST"}),
        ("list_spaces", {}),
        ("get_page_comments", {"page_id": "123"}),
        ("add_page_comment", {"page_id": "123", "comment": "test"}),
        ("get_page_attachments", {"page_id": "123"}),
        ("get_confluence_user", {"account_id": "123"}),
        ("search_confluence_users", {"query": "test"}),
        ("add_page_label", {"page_id": "123", "label": "test"}),
        ("get_page_labels", {"page_id": "123"}),
        ("get_page_history", {"page_id": "123"}),
        ("get_page_restrictions", {"page_id": "123"}),
        ("set_page_restrictions", {"page_id": "123", "restrictions": {}}),
        ("copy_page", {"page_id": "123", "new_title": "test"}),
        ("get_user_content", {"account_id": "123"}),
        ("get_recent_content", {}),
        ("restore_page_version", {"page_id": "123", "version": 1}),
        ("search_by_author", {"account_id": "123"}),
        ("search_by_label", {"label": "test"}),
        ("move_page", {"page_id": "123", "target_space_key": "TEST"}),
        ("get_child_pages", {"page_id": "123"}),
        ("get_descendants", {"page_id": "123"}),
        ("get_ancestors", {"page_id": "123"}),
        ("cql_search", {"cql": "type=page"}),
    ]
    
    for tool_name, args in tools:
        result = await route_tool_call(tool_name, args, jira, confluence, bitbucket)
        assert result == {"success": True}


# Bitbucket tools (33 total)
@pytest.mark.asyncio
async def test_bitbucket_tools(mock_providers):
    jira, confluence, bitbucket = mock_providers
    
    tools = [
        ("search_bitbucket", {"query": "test"}),
        ("get_repository", {"repo_slug": "repo"}),
        ("list_repositories", {}),
        ("list_pull_requests", {"repo_slug": "repo"}),
        ("get_pull_request", {"repo_slug": "repo", "pr_id": 1}),
        ("create_pull_request", {"repo_slug": "repo", "title": "test", "source_branch": "dev", "dest_branch": "main"}),
        ("get_file_content", {"repo_slug": "repo", "file_path": "test.txt"}),
        ("list_commits", {"repo_slug": "repo"}),
        ("get_commit", {"repo_slug": "repo", "commit_hash": "abc123"}),
        ("list_branches", {"repo_slug": "repo"}),
        ("get_pull_request_diff", {"repo_slug": "repo", "pr_id": 1}),
        ("get_pull_request_comments", {"repo_slug": "repo", "pr_id": 1}),
        ("add_pr_comment", {"repo_slug": "repo", "pr_id": 1, "comment": "test"}),
        ("approve_pull_request", {"repo_slug": "repo", "pr_id": 1}),
        ("merge_pull_request", {"repo_slug": "repo", "pr_id": 1}),
        ("get_commit_diff", {"repo_slug": "repo", "commit_hash": "abc123"}),
        ("list_tags", {"repo_slug": "repo"}),
        ("list_directory", {"repo_slug": "repo"}),
        ("update_pull_request", {"repo_slug": "repo", "pr_id": 1}),
        ("compare_commits", {"repo_slug": "repo", "from_commit": "abc123", "to_commit": "def456"}),
        ("add_pr_reviewer", {"repo_slug": "repo", "pr_id": 1, "account_id": "123"}),
        ("decline_pull_request", {"repo_slug": "repo", "pr_id": 1}),
        ("create_branch", {"repo_slug": "repo", "branch_name": "feature"}),
        ("delete_branch", {"repo_slug": "repo", "branch_name": "feature"}),
        ("get_bitbucket_user", {"username": "user"}),
        ("get_pr_activity", {"repo_slug": "repo", "pr_id": 1}),
        ("get_default_reviewers", {"repo_slug": "repo"}),
        ("list_pull_requests_by_author", {"repo_slug": "repo"}),
        ("list_commits_by_author", {"repo_slug": "repo", "author": "user"}),
        ("request_changes", {"repo_slug": "repo", "pr_id": 1}),
        ("get_branch_restrictions", {"repo_slug": "repo"}),
        ("get_build_status", {"repo_slug": "repo", "commit_hash": "abc123"}),
        ("create_webhook", {"repo_slug": "repo", "url": "https://example.com"}),
    ]
    
    for tool_name, args in tools:
        result = await route_tool_call(tool_name, args, jira, confluence, bitbucket)
        assert result == {"success": True}


# Ticket support tools (4 total)
@pytest.mark.asyncio
async def test_ticket_support_tools(mock_providers):
    jira, confluence, bitbucket = mock_providers
    
    with patch('mcp_server.common.ticket_support_tools.get_open_support_tickets', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"success": True}
        result = await route_tool_call("get_open_support_tickets", {}, jira, confluence, bitbucket)
        assert result == {"success": True}
    
    with patch('mcp_server.common.ticket_support_tools.check_ticket_template', new_callable=AsyncMock) as mock_check:
        mock_check.return_value = {"success": True}
        result = await route_tool_call("check_ticket_template", {"issue_key": "TEST-1"}, jira, confluence, bitbucket)
        assert result == {"success": True}
    
    with patch('mcp_server.common.ticket_support_tools.suggest_assignee', new_callable=AsyncMock) as mock_suggest:
        mock_suggest.return_value = {"success": True}
        result = await route_tool_call("suggest_assignee", {"issue_key": "TEST-1"}, jira, confluence, bitbucket)
        assert result == {"success": True}
    
    with patch('mcp_server.common.ticket_support_tools.get_team_workload', new_callable=AsyncMock) as mock_workload:
        mock_workload.return_value = {"success": True}
        result = await route_tool_call("get_team_workload", {}, jira, confluence, bitbucket)
        assert result == {"success": True}
