import pytest
from unittest.mock import Mock, patch
from mcp_server.datacenter.confluence_dc_provider import ConfluenceDCProvider


@pytest.fixture
def confluence_dc_provider():
    with patch('mcp_server.datacenter.confluence_dc_provider.DataCenterAuth'):
        provider = ConfluenceDCProvider()
        provider.auth.get_base_url = Mock(return_value="https://confluence.company.com")
        provider.auth.get_auth_headers = Mock(return_value={"Authorization": "Bearer token"})
        return provider


@pytest.fixture
def mock_response():
    response = Mock()
    response.raise_for_status = Mock()
    response.json = Mock(return_value={"id": "12345", "title": "Test Page"})
    return response


@pytest.mark.asyncio
async def test_get_page_success(confluence_dc_provider, mock_response):
    confluence_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await confluence_dc_provider.get_page("12345")
    
    assert result == {"id": "12345", "title": "Test Page"}
    confluence_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_page_invalid_id(confluence_dc_provider):
    result = await confluence_dc_provider.get_page("invalid")
    
    assert "error" in result
    assert "page_id must be numeric" in result["error"]


@pytest.mark.asyncio
async def test_create_page_success(confluence_dc_provider, mock_response):
    confluence_dc_provider.session.post = Mock(return_value=mock_response)
    
    result = await confluence_dc_provider.create_page("TEST", "Title", "<p>Content</p>")
    
    assert result == {"id": "12345", "title": "Test Page"}
    confluence_dc_provider.session.post.assert_called_once()


@pytest.mark.asyncio
async def test_create_page_invalid_space(confluence_dc_provider):
    result = await confluence_dc_provider.create_page("invalid", "Title", "Content")
    
    assert "error" in result
    assert "Invalid space_key format" in result["error"]


@pytest.mark.asyncio
async def test_search_success(confluence_dc_provider, mock_response):
    mock_response.json = Mock(return_value={
        "results": [{"content": {"type": "page", "title": "Test"}}]
    })
    confluence_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await confluence_dc_provider.search("test query")
    
    assert "results" in result
    assert len(result["results"]) == 1
    confluence_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_list_spaces_success(confluence_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"results": [{"key": "TEST"}]})
    confluence_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await confluence_dc_provider.list_spaces()
    
    assert "results" in result
    confluence_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_search_users_success(confluence_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"results": [{"username": "testuser", "displayName": "Test User"}]})
    confluence_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await confluence_dc_provider.search_users("test")
    
    assert "users" in result
    confluence_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_add_label_success(confluence_dc_provider, mock_response):
    confluence_dc_provider.session.post = Mock(return_value=mock_response)
    
    result = await confluence_dc_provider.add_label("12345", "test-label")
    
    assert result["success"] == True
    confluence_dc_provider.session.post.assert_called_once()


@pytest.mark.asyncio
async def test_get_page_history_success(confluence_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"results": [{"number": 1}]})
    confluence_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await confluence_dc_provider.get_page_history("12345")
    
    assert "results" in result
    confluence_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_copy_page_invalid_id(confluence_dc_provider):
    result = await confluence_dc_provider.copy_page("invalid", "TEAM123", "New Title")
    
    assert "error" in result
    assert "page_id must be numeric" in result["error"]


@pytest.mark.asyncio
async def test_get_user_content_success(confluence_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"results": [{"id": "123", "title": "Page"}]})
    confluence_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await confluence_dc_provider.get_user_content("testuser")
    
    assert "results" in result
    confluence_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_recent_content_success(confluence_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"results": [{"id": "123", "title": "Page"}]})
    confluence_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await confluence_dc_provider.get_recent_content()
    
    assert "results" in result
    confluence_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_restore_page_version_success(confluence_dc_provider, mock_response):
    from unittest.mock import AsyncMock
    mock_response.json = Mock(return_value={"id": "12345", "title": "Test", "body": {"storage": {"value": "<p>Old</p>"}}, "version": {"number": 2}})
    confluence_dc_provider.session.get = Mock(return_value=mock_response)
    confluence_dc_provider.session.put = Mock(return_value=mock_response)
    confluence_dc_provider.get_page = AsyncMock(return_value={"version": {"number": 3}})
    confluence_dc_provider.update_page = AsyncMock(return_value={"id": "12345"})
    
    result = await confluence_dc_provider.restore_page_version("12345", 2)
    
    assert result["id"] == "12345"


@pytest.mark.asyncio
async def test_search_by_author_success(confluence_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"results": [{"id": "123", "title": "Page"}]})
    confluence_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await confluence_dc_provider.search_by_author("testuser")
    
    assert "results" in result
    confluence_dc_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_search_by_label_success(confluence_dc_provider, mock_response):
    mock_response.json = Mock(return_value={"results": [{"id": "123", "title": "Page"}]})
    confluence_dc_provider.session.get = Mock(return_value=mock_response)
    
    result = await confluence_dc_provider.search_by_label("test-label")
    
    assert "results" in result
    confluence_dc_provider.session.get.assert_called_once()
