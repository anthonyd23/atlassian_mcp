import pytest
from unittest.mock import Mock, patch
from mcp_server.datacenter.jira_dc_provider import JiraDCProvider


@pytest.fixture
def jira_dc_provider():
    with patch('mcp_server.datacenter.jira_dc_provider.DataCenterAuth'):
        provider = JiraDCProvider()
        provider.base_url = "https://jira.company.com"
        provider.auth.get_auth_headers = Mock(return_value={"Authorization": "Bearer token"})
        return provider


@pytest.fixture
def mock_response():
    response = Mock()
    response.raise_for_status = Mock()
    response.json = Mock(return_value={"key": "TEST-123", "fields": {"summary": "Test"}})
    return response


@pytest.mark.asyncio
async def test_get_issue_success(jira_dc_provider, mock_response):
    jira_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await jira_dc_provider.get_issue("TEST-123")
    
    assert result == {"key": "TEST-123", "fields": {"summary": "Test"}}
    jira_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_issue_invalid_key(jira_dc_provider):
    result = await jira_dc_provider.get_issue("invalid")
    
    assert "error" in result
    assert "Invalid issue_key format" in result["error"]


@pytest.mark.asyncio
async def test_get_issue_api_error(jira_dc_provider):
    jira_dc_provider.session.get = Mock(side_effect=Exception("API Error"))
    
    result = await jira_dc_provider.get_issue("TEST-123")
    
    assert "error" in result
    assert "API Error" in result["error"]


@pytest.mark.asyncio
async def test_create_issue_success(jira_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"key": "TEST-124"})
    jira_dc_provider.session.post = Mock(return_value=mock_response)
    
    result = await jira_dc_provider.create_issue("TEST", "Summary", "Description")
    
    assert result == {"key": "TEST-124"}
    jira_dc_provider.session.post.assert_called_once()


@pytest.mark.asyncio
async def test_create_issue_invalid_project(jira_dc_provider):
    result = await jira_dc_provider.create_issue("invalid", "Summary", "Description")
    
    assert "error" in result
    assert "Invalid project_key format" in result["error"]


@pytest.mark.asyncio
async def test_search_success(jira_dc_provider, mock_response):
    mock_response.json = Mock(return_value={
        "total": 1,
        "issues": [{"key": "TEST-123", "fields": {"summary": "Test"}}]
    })
    jira_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await jira_dc_provider.search("project = TEST")
    
    assert result["total"] == 1
    assert len(result["results"]) == 1
    jira_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_list_projects_success(jira_dc_provider, mock_response):
    mock_response.json = Mock(return_value=[{"key": "TEST", "name": "Test Project"}])
    jira_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await jira_dc_provider.list_projects()
    
    assert "projects" in result
    assert len(result["projects"]) == 1
    jira_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_current_user_success(jira_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"name": "testuser", "displayName": "Test User"})
    jira_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await jira_dc_provider.get_current_user()
    
    assert result["name"] == "testuser"
    jira_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_search_users_success(jira_dc_provider, mock_response):
    mock_response.json = Mock(return_value=[{"name": "testuser", "displayName": "Test User"}])
    jira_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await jira_dc_provider.search_users("test")
    
    assert len(result["users"]) == 1
    jira_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_link_issues_success(jira_dc_provider, mock_response):
    jira_dc_provider.session.post = Mock(return_value=mock_response)
    
    result = await jira_dc_provider.link_issues("TEST-1", "TEST-2", "Relates")
    
    assert result["success"] == True
    jira_dc_provider.session.post.assert_called_once()


@pytest.mark.asyncio
async def test_add_worklog_success(jira_dc_provider, mock_response):
    jira_dc_provider.session.post = Mock(return_value=mock_response)
    
    result = await jira_dc_provider.add_worklog("TEST-123", "2h")
    
    assert result == {"key": "TEST-123", "fields": {"summary": "Test"}}
    jira_dc_provider.session.post.assert_called_once()


@pytest.mark.asyncio
async def test_set_priority_success(jira_dc_provider, mock_response):
    jira_dc_provider.session.put = Mock(return_value=mock_response)
    
    result = await jira_dc_provider.set_priority("TEST-123", "High")
    
    assert result["success"] == True
    jira_dc_provider.session.put.assert_called_once()


@pytest.mark.asyncio
async def test_list_boards_success(jira_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"id": 1, "name": "Test Board"}]})
    jira_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await jira_dc_provider.list_boards()
    
    assert "values" in result
    jira_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_board_issues_success(jira_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"issues": [{"key": "TEST-1"}]})
    jira_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await jira_dc_provider.get_board_issues(1)
    
    assert "issues" in result
    jira_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_list_sprints_success(jira_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"id": 1, "name": "Sprint 1"}]})
    jira_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await jira_dc_provider.list_sprints(1)
    
    assert "values" in result
    jira_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_sprint_issues_success(jira_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"issues": [{"key": "TEST-1"}]})
    jira_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await jira_dc_provider.get_sprint_issues(1)
    
    assert "issues" in result
    jira_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_permissions_success(jira_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"permissions": {"BROWSE_PROJECTS": {"havePermission": True}}})
    jira_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await jira_dc_provider.get_user_permissions("TEST")
    
    assert "permissions" in result
    jira_dc_provider.session.get.assert_called_once()
