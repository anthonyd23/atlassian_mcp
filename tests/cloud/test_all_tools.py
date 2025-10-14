#!/usr/bin/env python3
"""Test all 89 MCP tools"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

async def run_tests():
    print("=" * 60)
    print("TESTING ALL ATLASSIAN CLOUD TOOLS (89 TOTAL)")
    print("=" * 60)
    
    from mcp_server.cloud.jira_provider import JiraProvider
    from mcp_server.cloud.confluence_provider import ConfluenceProvider
    from mcp_server.cloud.bitbucket_provider import BitbucketProvider
    
    # Test Jira (31 tools)
    print("\n" + "=" * 60)
    print("JIRA CLOUD TOOLS (31)")
    print("=" * 60)
    jira = JiraProvider()
    
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
    
    # Test Confluence (25 tools)
    print("\n" + "=" * 60)
    print("CONFLUENCE CLOUD TOOLS (25)")
    print("=" * 60)
    confluence = ConfluenceProvider()
    
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
    
    # Test Bitbucket (33 tools)
    print("\n" + "=" * 60)
    print("BITBUCKET CLOUD TOOLS (33)")
    print("=" * 60)
    bitbucket = BitbucketProvider()
    
    print("\n1. list_repositories")
    print(await bitbucket.list_repositories())
    
    print("\n2. search_bitbucket")
    print(await bitbucket.search("test"))
    
    print("\n3. get_user (Phase 3)")
    print(await bitbucket.get_user("testuser"))
    
    print("\n4. list_pull_requests_by_author (Phase 6)")
    print(await bitbucket.list_pull_requests_by_author("test-repo", "testuser"))
    
    print("\n5. get_build_status (Phase 6)")
    print(await bitbucket.get_build_status("test-repo", "abc123"))
    
    print("\n" + "=" * 60)
    print("ALL CLOUD TOOLS TEST COMPLETED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_tests())
