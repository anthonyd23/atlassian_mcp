import pytest
from unittest.mock import Mock, AsyncMock
from mcp_server.common.router import route_tool_call


@pytest.fixture
def mock_providers():
    jira = Mock()
    jira.search = AsyncMock(return_value={"total": 1})
    jira.get_issue = AsyncMock(return_value={"key": "TEST-123"})
    jira.list_projects = AsyncMock(return_value={"projects": []})
    
    confluence = Mock()
    confluence.search = AsyncMock(return_value={"results": []})
    confluence.get_page = AsyncMock(return_value={"id": "123"})
    confluence.list_spaces = AsyncMock(return_value={"results": []})
    
    bitbucket = Mock()
    bitbucket.search = AsyncMock(return_value={"results": []})
    bitbucket.get_repository = AsyncMock(return_value={"slug": "repo"})
    bitbucket.list_repositories = AsyncMock(return_value={"values": []})
    
    return jira, confluence, bitbucket


@pytest.mark.asyncio
async def test_route_jira_search(mock_providers):
    jira, confluence, bitbucket = mock_providers
    
    result = await route_tool_call("search_jira", {"jql": "project = TEST"}, jira, confluence, bitbucket)
    
    assert result == {"total": 1}
    jira.search.assert_called_once_with("project = TEST")


@pytest.mark.asyncio
async def test_route_jira_get_issue(mock_providers):
    jira, confluence, bitbucket = mock_providers
    
    result = await route_tool_call("get_issue", {"issue_key": "TEST-123"}, jira, confluence, bitbucket)
    
    assert result == {"key": "TEST-123"}
    jira.get_issue.assert_called_once_with("TEST-123")


@pytest.mark.asyncio
async def test_route_confluence_search(mock_providers):
    jira, confluence, bitbucket = mock_providers
    
    result = await route_tool_call("search_confluence", {"query": "test"}, jira, confluence, bitbucket)
    
    assert result == {"results": []}
    confluence.search.assert_called_once_with("test")


@pytest.mark.asyncio
async def test_route_confluence_get_page(mock_providers):
    jira, confluence, bitbucket = mock_providers
    
    result = await route_tool_call("get_page", {"page_id": "123"}, jira, confluence, bitbucket)
    
    assert result == {"id": "123"}
    confluence.get_page.assert_called_once_with("123")


@pytest.mark.asyncio
async def test_route_bitbucket_search(mock_providers):
    jira, confluence, bitbucket = mock_providers
    
    result = await route_tool_call("search_bitbucket", {"query": "test"}, jira, confluence, bitbucket)
    
    assert result == {"results": []}
    bitbucket.search.assert_called_once_with("test")


@pytest.mark.asyncio
async def test_route_bitbucket_get_repository(mock_providers):
    jira, confluence, bitbucket = mock_providers
    
    result = await route_tool_call("get_repository", {"repo_slug": "repo"}, jira, confluence, bitbucket)
    
    assert result == {"slug": "repo"}
    bitbucket.get_repository.assert_called_once_with("repo")


@pytest.mark.asyncio
async def test_route_unknown_tool(mock_providers):
    jira, confluence, bitbucket = mock_providers
    
    with pytest.raises(ValueError, match="Unknown tool"):
        await route_tool_call("unknown_tool", {}, jira, confluence, bitbucket)
