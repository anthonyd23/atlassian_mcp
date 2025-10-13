import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from mcp_server.cloud.jira_provider import JiraProvider


@pytest.fixture
def jira_provider():
    with patch('mcp_server.cloud.jira_provider.Auth'):
        provider = JiraProvider()
        provider.auth.get_base_url = Mock(return_value="https://test.atlassian.net")
        provider.auth.get_auth_headers = Mock(return_value={"Authorization": "Bearer token"})
        return provider


@pytest.fixture
def mock_response():
    response = Mock()
    response.raise_for_status = Mock()
    response.json = Mock(return_value={"key": "TEST-123", "fields": {"summary": "Test"}})
    return response


@pytest.mark.asyncio
async def test_get_issue_success(jira_provider, mock_response):
    jira_provider.session.get = Mock(return_value=mock_response)
    
    result = await jira_provider.get_issue("TEST-123")
    
    assert result == {"key": "TEST-123", "fields": {"summary": "Test"}}
    jira_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_issue_invalid_key(jira_provider):
    result = await jira_provider.get_issue("invalid")
    
    assert "error" in result
    assert "Invalid issue_key format" in result["error"]


@pytest.mark.asyncio
async def test_get_issue_api_error(jira_provider):
    jira_provider.session.get = Mock(side_effect=Exception("API Error"))
    
    result = await jira_provider.get_issue("TEST-123")
    
    assert "error" in result
    assert "API Error" in result["error"]


@pytest.mark.asyncio
async def test_create_issue_success(jira_provider, mock_response):
    mock_response.json = Mock(return_value={"key": "TEST-124"})
    jira_provider.session.post = Mock(return_value=mock_response)
    
    result = await jira_provider.create_issue("TEST", "Summary", "Description")
    
    assert result == {"key": "TEST-124"}
    jira_provider.session.post.assert_called_once()


@pytest.mark.asyncio
async def test_create_issue_invalid_project(jira_provider):
    result = await jira_provider.create_issue("invalid", "Summary", "Description")
    
    assert "error" in result
    assert "Invalid project_key format" in result["error"]


@pytest.mark.asyncio
async def test_search_success(jira_provider, mock_response):
    mock_response.json = Mock(return_value={
        "total": 1,
        "issues": [{"key": "TEST-123", "fields": {"summary": "Test"}}]
    })
    jira_provider.session.post = Mock(return_value=mock_response)
    
    result = await jira_provider.search("project = TEST")
    
    assert result["total"] == 1
    assert len(result["results"]) == 1
    jira_provider.session.post.assert_called_once()


@pytest.mark.asyncio
async def test_list_projects_success(jira_provider, mock_response):
    mock_response.json = Mock(return_value=[{"key": "TEST", "name": "Test Project"}])
    jira_provider.session.get = Mock(return_value=mock_response)
    
    result = await jira_provider.list_projects()
    
    assert "projects" in result
    assert len(result["projects"]) == 1
    jira_provider.session.get.assert_called_once()
