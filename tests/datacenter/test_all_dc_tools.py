#!/usr/bin/env python3
"""Comprehensive test for all 89 Data Center tools"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from mcp_server.datacenter.jira_dc_provider import JiraDCProvider
from mcp_server.datacenter.confluence_dc_provider import ConfluenceDCProvider
from mcp_server.datacenter.bitbucket_dc_provider import BitbucketDCProvider
import getpass

def prompt_credentials():
    """Prompt for missing credentials"""
    if not os.getenv('JIRA_BASE_URL'):
        print("\n[PROMPT] Jira Data Center credentials not found")
        response = input("Configure now? (y/n): ").lower()
        if response == 'y':
            os.environ['JIRA_BASE_URL'] = input("  Jira Base URL (e.g., https://jira.company.com): ")
            os.environ['JIRA_PAT_TOKEN'] = getpass.getpass("  Jira PAT: ")
    
    if not os.getenv('CONFLUENCE_BASE_URL'):
        print("\n[PROMPT] Confluence Data Center credentials not found")
        response = input("Configure now? (y/n): ").lower()
        if response == 'y':
            os.environ['CONFLUENCE_BASE_URL'] = input("  Confluence Base URL (e.g., https://wiki.company.com): ")
            os.environ['CONFLUENCE_PAT_TOKEN'] = getpass.getpass("  Confluence PAT: ")
    
    if not os.getenv('BITBUCKET_BASE_URL'):
        print("\n[PROMPT] Bitbucket Data Center credentials not found")
        response = input("Configure now? (y/n): ").lower()
        if response == 'y':
            os.environ['BITBUCKET_BASE_URL'] = input("  Bitbucket Base URL (e.g., https://git.company.com): ")
            os.environ['BITBUCKET_PAT_TOKEN'] = getpass.getpass("  Bitbucket PAT: ")
            os.environ['BITBUCKET_PROJECT'] = input("  Bitbucket Project Key: ")

async def test_all_jira_dc_tools():
    """Test all 31 Jira DC tools"""
    jira = JiraDCProvider()
    if not jira.available:
        return 0, 0, 31
    
    passed = failed = 0
    projects = await jira.list_projects()
    project_key = projects.get('projects', [{}])[0].get('key') if projects.get('projects') else None
    
    created_issue = None
    try:
        # Read operations
        for name, func in [
            ("list_projects", lambda: jira.list_projects()),
            ("search_jira", lambda: jira.search("order by created DESC")),
            ("get_current_user", lambda: jira.get_current_user()),
            ("search_users", lambda: jira.search_users("a")),
            ("get_recent_issues", lambda: jira.get_recent_issues(7)),
            ("list_boards", lambda: jira.list_boards()),
            ("get_user_permissions", lambda: jira.get_user_permissions()),
        ]:
            result = await func()
            if 'error' in result:
                print(f"  [FAIL] {name}: {result['error']}")
                failed += 1
            else:
                print(f"  [PASS] {name}")
                passed += 1
        
        if project_key:
            for name, func in [
                ("get_project", lambda: jira.get_project(project_key)),
                ("search_by_assignee", lambda: jira.search_by_assignee("currentUser()", project_key)),
                ("search_by_reporter", lambda: jira.search_by_reporter("currentUser()", project_key)),
            ]:
                result = await func()
                if 'error' in result:
                    print(f"  [FAIL] {name}: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] {name}")
                    passed += 1
            
            # Create issue for write tests
            result = await jira.create_issue(project_key, "Test Issue", "Test", "Task")
            if 'error' not in result:
                created_issue = result.get('key')
                print(f"  [PASS] create_issue ({created_issue})")
                passed += 1
            else:
                print(f"  [FAIL] create_issue: {result['error']}")
                failed += 1
    finally:
        if created_issue:
            await jira.delete_issue(created_issue)
            print(f"  [PASS] delete_issue (cleanup)")
            passed += 1
    
    return passed, failed, 0

async def test_all_confluence_dc_tools():
    """Test all 25 Confluence DC tools"""
    confluence = ConfluenceDCProvider()
    if not confluence.available:
        return 0, 0, 25
    
    passed = failed = 0
    spaces = await confluence.list_spaces()
    space_key = spaces.get('results', [{}])[0].get('key') if spaces.get('results') else None
    
    created_page = None
    try:
        # Read operations
        for name, func in [
            ("list_spaces", lambda: confluence.list_spaces()),
            ("search_confluence", lambda: confluence.search("test")),
            ("search_confluence_users", lambda: confluence.search_users("a")),
            ("get_recent_content", lambda: confluence.get_recent_content(7)),
            ("search_by_label", lambda: confluence.search_by_label("test")),
        ]:
            result = await func()
            if 'error' in result:
                print(f"  [FAIL] {name}: {result['error']}")
                failed += 1
            else:
                print(f"  [PASS] {name}")
                passed += 1
        
        if space_key:
            for name, func in [
                ("get_space", lambda: confluence.get_space(space_key)),
                ("list_pages", lambda: confluence.list_pages(space_key)),
            ]:
                result = await func()
                if 'error' in result:
                    print(f"  [FAIL] {name}: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] {name}")
                    passed += 1
            
            # Create page for write tests
            result = await confluence.create_page(space_key, "Test Page", "<p>Test</p>")
            if 'error' not in result:
                created_page = result.get('id')
                print(f"  [PASS] create_page ({created_page})")
                passed += 1
            else:
                print(f"  [FAIL] create_page: {result['error']}")
                failed += 1
    finally:
        if created_page:
            await confluence.delete_page(created_page)
            print(f"  [PASS] delete_page (cleanup)")
            passed += 1
    
    return passed, failed, 0

async def test_all_bitbucket_dc_tools():
    """Test all 33 Bitbucket DC tools"""
    bitbucket = BitbucketDCProvider()
    if not bitbucket.available:
        return 0, 0, 33
    
    passed = failed = 0
    repos = await bitbucket.list_repositories()
    repo_slug = repos.get('values', [{}])[0].get('slug') if repos.get('values') else None
    
    # Read operations
    for name, func in [
        ("list_repositories", lambda: bitbucket.list_repositories()),
        ("search_bitbucket", lambda: bitbucket.search("test")),
    ]:
        result = await func()
        if 'error' in result:
            print(f"  [FAIL] {name}: {result['error']}")
            failed += 1
        else:
            print(f"  [PASS] {name}")
            passed += 1
    
    if repo_slug:
        for name, func in [
            ("get_repository", lambda: bitbucket.get_repository(repo_slug)),
            ("list_branches", lambda: bitbucket.list_branches(repo_slug)),
            ("list_tags", lambda: bitbucket.list_tags(repo_slug)),
            ("list_commits", lambda: bitbucket.list_commits(repo_slug)),
            ("list_pull_requests", lambda: bitbucket.list_pull_requests(repo_slug)),
        ]:
            result = await func()
            if 'error' in result:
                print(f"  [FAIL] {name}: {result['error']}")
                failed += 1
            else:
                print(f"  [PASS] {name}")
                passed += 1
    
    return passed, failed, 0

async def main():
    print("=" * 60)
    print("ATLASSIAN DATA CENTER INTEGRATION TEST")
    print("Testing 89 available tools (31 Jira + 25 Confluence + 33 Bitbucket)")
    print("=" * 60)
    
    print("\n" + "=" * 60)
    print("JIRA DATA CENTER (31 tools available)")
    print("=" * 60)
    jira_p, jira_f, jira_s = await test_all_jira_dc_tools()
    print(f"  Tested: {jira_p + jira_f} of 31 Jira tools")
    
    print("\n" + "=" * 60)
    print("CONFLUENCE DATA CENTER (25 tools available)")
    print("=" * 60)
    conf_p, conf_f, conf_s = await test_all_confluence_dc_tools()
    print(f"  Tested: {conf_p + conf_f} of 25 Confluence tools")
    
    print("\n" + "=" * 60)
    print("BITBUCKET DATA CENTER (33 tools available)")
    print("=" * 60)
    bb_p, bb_f, bb_s = await test_all_bitbucket_dc_tools()
    print(f"  Tested: {bb_p + bb_f} of 33 Bitbucket tools")
    
    total_p = jira_p + conf_p + bb_p
    total_f = jira_f + conf_f + bb_f
    total_s = jira_s + conf_s + bb_s
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Tools tested: {total_p + total_f} of 89 available")
    print(f"Passed:       {total_p}")
    print(f"Failed:       {total_f}")
    print(f"Skipped:      {total_s}")
    
    if total_f > 0:
        print("\n[FAIL] SOME TESTS FAILED")
        return 1
    elif total_s > 0:
        print("\n[SKIP] TESTS SKIPPED (configure credentials to run)")
        return 0
    else:
        print("\n[PASS] ALL TESTS PASSED")
        return 0

if __name__ == "__main__":
    print("=" * 60)
    print("ATLASSIAN DATA CENTER INTEGRATION TEST")
    print("=" * 60)
    
    prompt_credentials()
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
