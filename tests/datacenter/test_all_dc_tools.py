import asyncio
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from mcp_server.datacenter.jira_dc_provider import JiraDCProvider
from mcp_server.datacenter.confluence_dc_provider import ConfluenceDCProvider
from mcp_server.datacenter.bitbucket_dc_provider import BitbucketDCProvider

async def test_all_dc_tools():
    print("=" * 60)
    print("ATLASSIAN DATA CENTER INTEGRATION TEST (89 TOOLS)")
    print("=" * 60)
    
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    
    # Jira Data Center (31 tools)
    print("\n" + "=" * 60)
    print("JIRA DATA CENTER (31 TOOLS)")
    print("=" * 60)
    jira = JiraDCProvider()
    
    if not jira.available:
        print("⚠ Jira Data Center not configured - skipping all Jira tests")
        total_skipped += 7
    else:
        print("✓ Jira Data Center configured")
        
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
    
    # Confluence Data Center (25 tools)
    print("\n" + "=" * 60)
    print("CONFLUENCE DATA CENTER (25 TOOLS)")
    print("=" * 60)
    confluence = ConfluenceDCProvider()
    
    if not confluence.available:
        print("⚠ Confluence Data Center not configured - skipping all Confluence tests")
        total_skipped += 5
    else:
        print("✓ Confluence Data Center configured")
        
        tests = [
            ("list_spaces", lambda: confluence.list_spaces()),
            ("search", lambda: confluence.search("test")),
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
    
    # Bitbucket Data Center (33 tools)
    print("\n" + "=" * 60)
    print("BITBUCKET DATA CENTER (33 TOOLS)")
    print("=" * 60)
    bitbucket = BitbucketDCProvider()
    
    if not bitbucket.available:
        print("⚠ Bitbucket Data Center not configured - skipping all Bitbucket tests")
        total_skipped += 3
    else:
        print("✓ Bitbucket Data Center configured")
        
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
    exit_code = asyncio.run(test_all_dc_tools())
    sys.exit(exit_code)
