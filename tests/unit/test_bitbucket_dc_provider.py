import pytest
from unittest.mock import Mock, patch
from mcp_server.datacenter.bitbucket_dc_provider import BitbucketDCProvider


@pytest.fixture
def bitbucket_dc_provider():
    with patch('mcp_server.datacenter.bitbucket_dc_provider.DataCenterAuth'):
        with patch.dict('os.environ', {'BITBUCKET_PROJECT': 'PROJ'}):
            provider = BitbucketDCProvider()
            provider.base_url = "https://bitbucket.company.com"
            provider.auth.get_auth_headers = Mock(return_value={"Authorization": "Bearer token"})
            return provider


@pytest.fixture
def mock_response():
    response = Mock()
    response.raise_for_status = Mock()
    response.json = Mock(return_value={"slug": "test-repo", "name": "Test Repo"})
    return response


@pytest.mark.asyncio
async def test_get_repository_success(bitbucket_dc_provider, mock_response):
    bitbucket_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_dc_provider.get_repository("test-repo")
    
    assert result == {"slug": "test-repo", "name": "Test Repo"}
    bitbucket_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_repository_invalid_slug(bitbucket_dc_provider):
    result = await bitbucket_dc_provider.get_repository("INVALID")
    
    assert "error" in result
    assert "Invalid repo_slug format" in result["error"]


@pytest.mark.asyncio
async def test_list_repositories_success(bitbucket_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"slug": "repo1"}]})
    bitbucket_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_dc_provider.list_repositories()
    
    assert "values" in result
    bitbucket_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_pull_request_success(bitbucket_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"id": 1, "title": "Test PR"})
    bitbucket_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_dc_provider.get_pull_request("test-repo", 1)
    
    assert result == {"id": 1, "title": "Test PR"}
    bitbucket_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_pull_request_invalid_id(bitbucket_dc_provider):
    result = await bitbucket_dc_provider.get_pull_request("test-repo", -1)
    
    assert "error" in result
    assert "pr_id must be a positive integer" in result["error"]


@pytest.mark.asyncio
async def test_create_pull_request_success(bitbucket_dc_provider, mock_response):
    bitbucket_dc_provider.session.post = Mock(return_value=mock_response)
    
    result = await bitbucket_dc_provider.create_pull_request("test-repo", "Title", "feature", "main")
    
    assert result == {"slug": "test-repo", "name": "Test Repo"}
    bitbucket_dc_provider.session.post.assert_called_once()


@pytest.mark.asyncio
async def test_search_success(bitbucket_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"name": "test-repo"}]})
    bitbucket_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_dc_provider.search("test")
    
    assert "results" in result
    bitbucket_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_add_pr_reviewer_invalid_id(bitbucket_dc_provider):
    result = await bitbucket_dc_provider.add_pr_reviewer("test-repo", -1, "testuser")
    
    assert "error" in result
    assert "pr_id must be a positive integer" in result["error"]


@pytest.mark.asyncio
async def test_decline_pull_request_invalid_id(bitbucket_dc_provider):
    result = await bitbucket_dc_provider.decline_pull_request("test-repo", -1)
    
    assert "error" in result
    assert "pr_id must be a positive integer" in result["error"]


@pytest.mark.asyncio
async def test_create_branch_success(bitbucket_dc_provider, mock_response):
    bitbucket_dc_provider.session.post = Mock(return_value=mock_response)
    
    result = await bitbucket_dc_provider.create_branch("test-repo", "feature-branch", "main")
    
    assert result == {"slug": "test-repo", "name": "Test Repo"}
    bitbucket_dc_provider.session.post.assert_called_once()


@pytest.mark.asyncio
async def test_delete_branch_success(bitbucket_dc_provider, mock_response):
    bitbucket_dc_provider.session.delete = Mock(return_value=mock_response)
    
    result = await bitbucket_dc_provider.delete_branch("test-repo", "feature-branch")
    
    assert result["success"] == True
    bitbucket_dc_provider.session.delete.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_success(bitbucket_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"name": "testuser", "displayName": "Test User"})
    bitbucket_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_dc_provider.get_user("testuser")
    
    assert result["name"] == "testuser"
    bitbucket_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_pr_activity_success(bitbucket_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"action": "APPROVED"}]})
    bitbucket_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_dc_provider.get_pr_activity("test-repo", 1)
    
    assert "values" in result
    bitbucket_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_default_reviewers_success(bitbucket_dc_provider, mock_response):
    mock_response.json = Mock(return_value=[{"name": "reviewer1"}])
    bitbucket_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_dc_provider.get_default_reviewers("test-repo")
    
    assert isinstance(result, list)
    bitbucket_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_list_pull_requests_by_author_success(bitbucket_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"id": 1, "author": {"user": {"name": "testuser"}}}]})
    bitbucket_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_dc_provider.list_pull_requests_by_author("test-repo", "testuser")
    
    assert "values" in result
    bitbucket_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_list_commits_by_author_success(bitbucket_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"id": "abc123", "author": {"name": "testuser"}}]})
    bitbucket_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_dc_provider.list_commits_by_author("test-repo", "testuser")
    
    assert "values" in result
    bitbucket_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_request_changes_success(bitbucket_dc_provider, mock_response):
    bitbucket_dc_provider.session.put = Mock(return_value=mock_response)
    
    result = await bitbucket_dc_provider.request_changes("test-repo", 1)
    
    assert result["success"] == True
    bitbucket_dc_provider.session.put.assert_called_once()


@pytest.mark.asyncio
async def test_get_branch_restrictions_success(bitbucket_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"type": "fast-forward-only", "matcher": {"id": "main"}}]})
    bitbucket_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_dc_provider.get_branch_restrictions("test-repo")
    
    assert "values" in result
    bitbucket_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_build_status_success(bitbucket_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"state": "SUCCESSFUL", "key": "build-1"}]})
    bitbucket_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_dc_provider.get_build_status("test-repo", "abc1234")
    
    assert "values" in result
    bitbucket_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_create_webhook_success(bitbucket_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"id": 1, "url": "https://example.com/hook"})
    bitbucket_dc_provider.session.post = Mock(return_value=mock_response)
    
    result = await bitbucket_dc_provider.create_webhook("test-repo", "https://example.com/hook", ["repo:refs_changed"])
    
    assert result["url"] == "https://example.com/hook"
    bitbucket_dc_provider.session.post.assert_called_once()
