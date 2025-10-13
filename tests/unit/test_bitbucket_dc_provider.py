import pytest
from unittest.mock import Mock, patch
from mcp_server.datacenter.bitbucket_dc_provider import BitbucketDCProvider


@pytest.fixture
def bitbucket_dc_provider():
    with patch('mcp_server.datacenter.bitbucket_dc_provider.DataCenterAuth'):
        with patch.dict('os.environ', {'BITBUCKET_PROJECT': 'PROJ'}):
            provider = BitbucketDCProvider()
            provider.auth.get_base_url = Mock(return_value="https://bitbucket.company.com")
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
