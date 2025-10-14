import asyncio
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from mcp_server.datacenter.jira_dc_provider import JiraDCProvider
from mcp_server.datacenter.confluence_dc_provider import ConfluenceDCProvider
from mcp_server.datacenter.bitbucket_dc_provider import BitbucketDCProvider

async def test_all_dc_tools():
    print("=" * 60)
    print("TESTING ALL ATLASSIAN DATA CENTER TOOLS (89 TOTAL)")
    print("=" * 60)
    
    # Jira Data Center (31 tools)
    print("\n" + "=" * 60)
    print("JIRA DATA CENTER TOOLS (31)")
    print("=" * 60)
    jira = JiraDCProvider()
    
    print("\n1. list_projects")
    print(await jira.list_projects())
    
    print("\n2. search_jira")
    print(await jira.search("project = TEST"))
    
    print("\n3. get_current_user (Phase 1)")
    print(await jira.get_current_user())
    
    print("\n4. search_users (Phase 1)")
    print(await jira.search_users("test"))
    
    print("\n5. get_recent_issues (Phase 3)")
    print(await jira.get_recent_issues())
    
    print("\n6. list_boards (Phase 4)")
    print(await jira.list_boards())
    
    print("\n7. get_user_permissions (Phase 5)")
    print(await jira.get_user_permissions())
    
    print("\n8. add_attachment (Phase 6)")
    print(await jira.add_attachment("TEST-1", "test.txt", b"test content"))
    
    # Confluence Data Center (25 tools)
    print("\n" + "=" * 60)
    print("CONFLUENCE DATA CENTER TOOLS (25)")
    print("=" * 60)
    confluence = ConfluenceDCProvider()
    
    print("\n1. list_spaces")
    print(await confluence.list_spaces())
    
    print("\n2. search_confluence")
    print(await confluence.search("test"))
    
    print("\n3. search_users (Phase 2)")
    print(await confluence.search_users("test"))
    
    print("\n4. get_recent_content (Phase 4)")
    print(await confluence.get_recent_content())
    
    print("\n5. search_by_label (Phase 5)")
    print(await confluence.search_by_label("test"))
    
    # Bitbucket Data Center (33 tools)
    print("\n" + "=" * 60)
    print("BITBUCKET DATA CENTER TOOLS (33)")
    print("=" * 60)
    bitbucket = BitbucketDCProvider()
    
    print("\n1. list_repositories")
    print(await bitbucket.list_repositories())
    
    print("\n2. search_bitbucket")
    print(await bitbucket.search("test"))
    
    print("\n3. get_user (Phase 3)")
    print(await bitbucket.get_user("testuser"))
    
    print("\n4. list_commits_by_author (Phase 6)")
    print(await bitbucket.list_commits_by_author("test-repo", "testuser"))
    
    print("\n5. get_branch_restrictions (Phase 6)")
    print(await bitbucket.get_branch_restrictions("test-repo"))
    
    print("\n" + "=" * 60)
    print("ALL DATA CENTER TOOLS TEST COMPLETED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_all_dc_tools())
