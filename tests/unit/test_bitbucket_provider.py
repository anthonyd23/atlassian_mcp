import pytest
from unittest.mock import Mock, patch
from mcp_server.cloud.bitbucket_provider import BitbucketProvider


@pytest.fixture
def bitbucket_provider():
    with patch('mcp_server.cloud.bitbucket_provider.CloudAuth'):
        with patch.dict('os.environ', {'BITBUCKET_API_TOKEN': 'token', 'BITBUCKET_WORKSPACE': 'workspace'}):
            provider = BitbucketProvider()
            provider.auth.username = "user@test.com"
            return provider


@pytest.fixture
def mock_response():
    response = Mock()
    response.raise_for_status = Mock()
    response.json = Mock(return_value={"slug": "test-repo", "name": "Test Repo"})
    return response


@pytest.mark.asyncio
async def test_get_repository_success(bitbucket_provider, mock_response):
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.get_repository("test-repo")
    
    assert result == {"slug": "test-repo", "name": "Test Repo"}
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_repository_invalid_slug(bitbucket_provider):
    result = await bitbucket_provider.get_repository("INVALID")
    
    assert "error" in result
    assert "Invalid repo_slug format" in result["error"]


@pytest.mark.asyncio
async def test_list_repositories_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"slug": "repo1"}]})
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.list_repositories()
    
    assert "values" in result
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_pull_request_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"id": 1, "title": "Test PR"})
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.get_pull_request("test-repo", 1)
    
    assert result == {"id": 1, "title": "Test PR"}
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_pull_request_invalid_id(bitbucket_provider):
    result = await bitbucket_provider.get_pull_request("test-repo", -1)
    
    assert "error" in result
    assert "pr_id must be a positive integer" in result["error"]


@pytest.mark.asyncio
async def test_create_pull_request_success(bitbucket_provider, mock_response):
    bitbucket_provider.session.post = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.create_pull_request("test-repo", "Title", "feature", "main")
    
    assert result == {"slug": "test-repo", "name": "Test Repo"}
    bitbucket_provider.session.post.assert_called_once()


@pytest.mark.asyncio
async def test_search_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"name": "test-repo"}]})
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.search("test")
    
    assert "results" in result
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_add_pr_reviewer_success(bitbucket_provider, mock_response):
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    bitbucket_provider.session.put = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.add_pr_reviewer("test-repo", 1, "account123")
    
    assert result["success"] == True
    bitbucket_provider.session.put.assert_called_once()


@pytest.mark.asyncio
async def test_decline_pull_request_success(bitbucket_provider, mock_response):
    bitbucket_provider.session.post = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.decline_pull_request("test-repo", 1)
    
    assert result["success"] == True
    bitbucket_provider.session.post.assert_called_once()


@pytest.mark.asyncio
async def test_create_branch_success(bitbucket_provider, mock_response):
    bitbucket_provider.session.post = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.create_branch("test-repo", "feature-branch", "main")
    
    assert result == {"slug": "test-repo", "name": "Test Repo"}
    bitbucket_provider.session.post.assert_called_once()


@pytest.mark.asyncio
async def test_delete_branch_success(bitbucket_provider, mock_response):
    bitbucket_provider.session.delete = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.delete_branch("test-repo", "feature-branch")
    
    assert result["success"] == True
    bitbucket_provider.session.delete.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"username": "testuser", "display_name": "Test User"})
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.get_user("testuser")
    
    assert result["username"] == "testuser"
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_pr_activity_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"update": {"state": "APPROVED"}}]})
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.get_pr_activity("test-repo", 1)
    
    assert "values" in result
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_default_reviewers_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"username": "reviewer1"}]})
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.get_default_reviewers("test-repo")
    
    assert "values" in result
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_list_pull_requests_by_author_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"id": 1, "author": {"username": "testuser"}}]})
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.list_pull_requests_by_author("test-repo", "testuser")
    
    assert "values" in result
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_list_commits_by_author_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"hash": "abc123", "author": {"user": {"username": "testuser"}}}]})
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.list_commits_by_author("test-repo", "testuser")
    
    assert "values" in result
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_request_changes_success(bitbucket_provider, mock_response):
    bitbucket_provider.session.post = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.request_changes("test-repo", 1)
    
    assert result["success"] == True
    bitbucket_provider.session.post.assert_called_once()


@pytest.mark.asyncio
async def test_get_branch_restrictions_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"kind": "push", "pattern": "main"}]})
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.get_branch_restrictions("test-repo")
    
    assert "values" in result
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_build_status_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"state": "SUCCESSFUL", "key": "build-1"}]})
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.get_build_status("test-repo", "abc1234")
    
    assert "values" in result
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_create_webhook_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"uuid": "{123}", "url": "https://example.com/hook"})
    bitbucket_provider.session.post = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.create_webhook("test-repo", "https://example.com/hook", ["repo:push"])
    
    assert result["url"] == "https://example.com/hook"
    bitbucket_provider.session.post.assert_called_once()


@pytest.mark.asyncio
async def test_list_pull_requests_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"id": 1, "title": "Test PR"}]})
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.list_pull_requests("test-repo")
    
    assert "values" in result
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_list_branches_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"name": "main"}]})
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.list_branches("test-repo")
    
    assert "values" in result
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_list_tags_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"name": "v1.0"}]})
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.list_tags("test-repo")
    
    assert "values" in result
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_list_commits_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"hash": "abc123"}]})
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.list_commits("test-repo")
    
    assert "values" in result
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_commit_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"hash": "abc1234", "message": "Test commit"})
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.get_commit("test-repo", "abc1234")
    
    assert result["hash"] == "abc1234"
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_commit_diff_success(bitbucket_provider, mock_response):
    mock_response.text = "diff --git a/file.txt b/file.txt"
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.get_commit_diff("test-repo", "abc1234")
    
    assert "diff" in result
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_pull_request_diff_success(bitbucket_provider, mock_response):
    mock_response.text = "diff --git a/file.txt b/file.txt"
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.get_pull_request_diff("test-repo", 1)
    
    assert "diff" in result
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_pull_request_comments_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"id": 1, "content": {"raw": "Comment"}}]})
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.get_pull_request_comments("test-repo", 1)
    
    assert "values" in result
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_add_pr_comment_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"id": 1, "content": {"raw": "Test comment"}})
    bitbucket_provider.session.post = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.add_pr_comment("test-repo", 1, "Test comment")
    
    assert result["id"] == 1
    bitbucket_provider.session.post.assert_called_once()


@pytest.mark.asyncio
async def test_approve_pull_request_success(bitbucket_provider, mock_response):
    bitbucket_provider.session.post = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.approve_pull_request("test-repo", 1)
    
    assert result["success"] == True
    bitbucket_provider.session.post.assert_called_once()


@pytest.mark.asyncio
async def test_merge_pull_request_success(bitbucket_provider, mock_response):
    bitbucket_provider.session.post = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.merge_pull_request("test-repo", 1)
    
    assert result == {"slug": "test-repo", "name": "Test Repo"}
    bitbucket_provider.session.post.assert_called_once()


@pytest.mark.asyncio
async def test_update_pull_request_success(bitbucket_provider, mock_response):
    bitbucket_provider.session.put = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.update_pull_request("test-repo", 1, "Updated Title")
    
    assert result == {"slug": "test-repo", "name": "Test Repo"}
    bitbucket_provider.session.put.assert_called_once()


@pytest.mark.asyncio
async def test_compare_commits_success(bitbucket_provider, mock_response):
    mock_response.text = "diff --git a/file.txt b/file.txt"
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.compare_commits("test-repo", "abc1234", "def5678")
    
    assert "diff" in result
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_file_content_success(bitbucket_provider, mock_response):
    mock_response.text = "file content"
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.get_file_content("test-repo", "README.md")
    
    assert result["content"] == "file content"
    bitbucket_provider.session.get.assert_called_once()


@pytest.mark.asyncio
async def test_list_directory_success(bitbucket_provider, mock_response):
    mock_response.json = Mock(return_value={"values": [{"path": "file.txt", "type": "commit_file"}]})
    bitbucket_provider.session.get = Mock(return_value=mock_response)
    
    result = await bitbucket_provider.list_directory("test-repo")
    
    assert "values" in result
    bitbucket_provider.session.get.assert_called_once()
