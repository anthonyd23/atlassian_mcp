import pytest
from unittest.mock import Mock, patch
from mcp_server.cloud.confluence_provider import ConfluenceProvider


@pytest.fixture
def confluence_provider():
    with patch('mcp_server.cloud.confluence_provider.Auth'):
        provider = ConfluenceProvider()
        provider.auth.get_base_url = Mock(return_value="https://test.atlassian.net")
        provider.auth.get_auth_headers = Mock(return_value={"Authorization": "Bearer token"})
        return provider


@pytest.fixture
def mock_response():
    response = Mock()
    response.raise_for_status = Mock()
    response.json = Mock(return_value={"id": "12345", "title": "Test Page"})
    return response


@pytest.mark.asyncio
async def test_get_page_success(confluence_provider, mock_response):
    confluence_provider.session.get = Mock(return_value=mock_response)
    
    result = await confluence_provider.get_page("12345")
    
    assert result == {"id": "12345", "title": "Test Page"}
    confluence_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_page_invalid_id(confluence_provider):
    result = await confluence_provider.get_page("invalid")
    
    assert "error" in result
    assert "page_id must be numeric" in result["error"]


@pytest.mark.asyncio
async def test_create_page_success(confluence_provider, mock_response):
    confluence_provider.session.post = Mock(return_value=mock_response)
    
    result = await confluence_provider.create_page("TEST", "Title", "<p>Content</p>")
    
    assert result == {"id": "12345", "title": "Test Page"}
    confluence_provider.session.post.assert_called_once()


@pytest.mark.asyncio
async def test_create_page_invalid_space(confluence_provider):
    result = await confluence_provider.create_page("invalid", "Title", "Content")
    
    assert "error" in result
    assert "Invalid space_key format" in result["error"]


@pytest.mark.asyncio
async def test_search_success(confluence_provider, mock_response):
    mock_response.json = Mock(return_value={
        "results": [{"content": {"type": "page", "title": "Test"}}]
    })
    confluence_provider.session.get = Mock(return_value=mock_response)
    
    result = await confluence_provider.search("test query")
    
    assert "results" in result
    assert len(result["results"]) == 1
    confluence_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_list_spaces_success(confluence_provider, mock_response):
    mock_response.json = Mock(return_value={"results": [{"key": "TEST"}]})
    confluence_provider.session.get = Mock(return_value=mock_response)
    
    result = await confluence_provider.list_spaces()
    
    assert "results" in result
    confluence_provider.session.get.assert_called_once()
