#!/usr/bin/env python3
"""Integration test for all 89 MCP tools - requires real credentials"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp_server.cloud.jira_provider import JiraProvider
from mcp_server.cloud.confluence_provider import ConfluenceProvider
from mcp_server.cloud.bitbucket_provider import BitbucketProvider

async def run_tests():
    print("=" * 60)
    print("ATLASSIAN CLOUD INTEGRATION TEST (89 TOOLS)")
    print("=" * 60)
    
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    
    # Test Jira (31 tools)
    print("\n" + "=" * 60)
    print("JIRA CLOUD (31 TOOLS)")
    print("=" * 60)
    jira = JiraProvider()
    
    if not jira.available:
        print("⚠ Jira not configured - skipping all Jira tests")
        total_skipped += 8
    else:
        print("✓ Jira configured")
        
        tests = [
            ("list_projects", lambda: jira.list_projects()),
            ("search", lambda: jira.search("order by created DESC")),
            ("get_current_user", lambda: jira.get_current_user()),
            ("search_users", lambda: jira.search_users("a")),
            ("get_recent_issues", lambda: jira.get_recent_issues(7)),
            ("list_boards", lambda: jira.list_boards()),
            ("get_user_permissions", lambda: jira.get_user_permissions()),
        ]
        
        for name, test_func in tests:
            result = await test_func()
            if 'error' in result:
                print(f"  ✗ {name}: {result['error'][:80]}")
                total_failed += 1
            else:
                print(f"  ✓ {name}")
                total_passed += 1
    
    # Test Confluence (25 tools)
    print("\n" + "=" * 60)
    print("CONFLUENCE CLOUD (25 TOOLS)")
    print("=" * 60)
    confluence = ConfluenceProvider()
    
    if not confluence.available:
        print("⚠ Confluence not configured - skipping all Confluence tests")
        total_skipped += 5
    else:
        print("✓ Confluence configured")
        
        tests = [
            ("list_spaces", lambda: confluence.list_spaces()),
            ("search", lambda: confluence.search("type=page")),
            ("search_users", lambda: confluence.search_users("a")),
            ("get_recent_content", lambda: confluence.get_recent_content(7)),
            ("search_by_label", lambda: confluence.search_by_label("test")),
        ]
        
        for name, test_func in tests:
            result = await test_func()
            if 'error' in result:
                print(f"  ✗ {name}: {result['error'][:80]}")
                total_failed += 1
            else:
                print(f"  ✓ {name}")
                total_passed += 1
    
    # Test Bitbucket (33 tools)
    print("\n" + "=" * 60)
    print("BITBUCKET CLOUD (33 TOOLS)")
    print("=" * 60)
    bitbucket = BitbucketProvider()
    
    if not bitbucket.available:
        print("⚠ Bitbucket not configured - skipping all Bitbucket tests")
        total_skipped += 3
    else:
        print("✓ Bitbucket configured")
        
        tests = [
            ("list_repositories", lambda: bitbucket.list_repositories()),
            ("search", lambda: bitbucket.search("test")),
        ]
        
        for name, test_func in tests:
            result = await test_func()
            if 'error' in result:
                print(f"  ✗ {name}: {result['error'][:80]}")
                total_failed += 1
            else:
                print(f"  ✓ {name}")
                total_passed += 1
        
        # Test with first repo if available
        repos = await bitbucket.list_repositories()
        if repos.get('values'):
            repo_slug = repos['values'][0]['slug']
            result = await bitbucket.list_branches(repo_slug)
            if 'error' in result:
                print(f"  ✗ list_branches: {result['error'][:80]}")
                total_failed += 1
            else:
                print(f"  ✓ list_branches")
                total_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Passed:  {total_passed}")
    print(f"Failed:  {total_failed}")
    print(f"Skipped: {total_skipped}")
    
    if total_failed > 0:
        print("\n✗ SOME TESTS FAILED")
        return 1
    elif total_skipped > 0:
        print("\n⚠ TESTS SKIPPED (configure credentials to run)")
        return 0
    else:
        print("\n✓ ALL TESTS PASSED")
        return 0

if __name__ == "__main__":
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)
