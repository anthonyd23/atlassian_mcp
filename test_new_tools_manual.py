#!/usr/bin/env python3
"""Manual test script for new Phase 1-3 tools using actual connections"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server.cloud.jira_provider import JiraProvider
from mcp_server.cloud.confluence_provider import ConfluenceProvider
from mcp_server.cloud.bitbucket_provider import BitbucketProvider

async def test_jira_new_tools():
    print("\n" + "=" * 60)
    print("TESTING NEW JIRA TOOLS")
    print("=" * 60)
    
    jira = JiraProvider()
    if not jira.available:
        print("WARNING: Jira not configured - skipping")
        return
    
    # Phase 1: User tools
    print("\n[Phase 1] get_current_user:")
    result = await jira.get_current_user()
    print(f"✓ Current user: {result.get('displayName', result.get('name', 'N/A'))}")
    
    print("\n[Phase 1] search_users:")
    result = await jira.search_users("a")
    print(f"✓ Found {len(result.get('users', []))} users")
    
    # Phase 1: Issue operations (read-only tests)
    print("\n[Phase 1] get_worklogs (if issue exists):")
    issues = await jira.get_recent_issues(days=30)
    if issues.get('results'):
        issue_key = issues['results'][0]['key']
        result = await jira.get_worklogs(issue_key)
        print(f"✓ Worklogs for {issue_key}: {len(result.get('worklogs', []))} entries")
    
    # Phase 3: Advanced search
    print("\n[Phase 3] get_recent_issues:")
    result = await jira.get_recent_issues(days=7)
    print(f"✓ Recent issues: {len(result.get('results', []))} found")
    
    print("\n[Phase 3] search_by_assignee:")
    users = await jira.search_users("a")
    if users.get('users'):
        assignee = users['users'][0].get('accountId') or users['users'][0].get('name')
        result = await jira.search_by_assignee(assignee)
        print(f"✓ Issues by assignee: {len(result.get('results', []))} found")

async def test_confluence_new_tools():
    print("\n" + "=" * 60)
    print("TESTING NEW CONFLUENCE TOOLS")
    print("=" * 60)
    
    confluence = ConfluenceProvider()
    if not confluence.available:
        print("WARNING: Confluence not configured - skipping")
        return
    
    # Phase 2: User tools
    print("\n[Phase 2] search_users:")
    result = await confluence.search_users("a")
    print(f"✓ Found {len(result.get('users', []))} users")
    
    # Phase 2: Content operations (read-only tests)
    print("\n[Phase 2] get_labels (if page exists):")
    pages = await confluence.search("type=page")
    if pages.get('results') and len(pages['results']) > 0:
        page_id = pages['results'][0].get('content', {}).get('id')
        if page_id:
            result = await confluence.get_labels(page_id)
            print(f"✓ Labels for page {page_id}: {len(result.get('results', []))} labels")
        else:
            print("  No page ID found")
    else:
        print("  No pages found")
    
    # Phase 3: Page history
    print("\n[Phase 3] get_page_history (if page exists):")
    if pages.get('results') and len(pages['results']) > 0:
        page_id = pages['results'][0].get('content', {}).get('id')
        if page_id:
            result = await confluence.get_page_history(page_id)
            print(f"✓ Page history: {len(result.get('results', []))} versions")
        else:
            print("  No page ID found")
    else:
        print("  No pages found")
    
    # Phase 3: Permissions
    print("\n[Phase 3] get_page_restrictions (if page exists):")
    if pages.get('results') and len(pages['results']) > 0:
        page_id = pages['results'][0].get('content', {}).get('id')
        if page_id:
            result = await confluence.get_page_restrictions(page_id)
            print(f"✓ Page restrictions retrieved")
        else:
            print("  No page ID found")
    else:
        print("  No pages found")

async def test_bitbucket_new_tools():
    print("\n" + "=" * 60)
    print("TESTING NEW BITBUCKET TOOLS")
    print("=" * 60)
    
    bitbucket = BitbucketProvider()
    if not bitbucket.available:
        print("WARNING: Bitbucket not configured - skipping")
        return
    
    # Get a repo to test with
    repos = await bitbucket.list_repositories()
    if not repos.get('values'):
        print("WARNING: No repositories found - skipping")
        return
    
    repo_slug = repos['values'][0]['slug']
    print(f"\nUsing repository: {repo_slug}")
    
    # Phase 3: User tools
    print("\n[Phase 3] get_user:")
    result = await bitbucket.get_user(bitbucket.auth.username)
    print(f"✓ User info: {result.get('display_name', result.get('username', 'N/A'))}")
    
    # Phase 3: PR activity
    print("\n[Phase 3] get_pr_activity (if PR exists):")
    prs = await bitbucket.list_pull_requests(repo_slug, state="MERGED")
    if prs.get('values') and len(prs['values']) > 0:
        pr_id = prs['values'][0]['id']
        result = await bitbucket.get_pr_activity(repo_slug, pr_id)
        print(f"✓ PR #{pr_id} activity: {len(result.get('values', []))} events")
    else:
        print("  No merged PRs found")
    
    # Phase 3: Default reviewers
    print("\n[Phase 3] get_default_reviewers:")
    result = await bitbucket.get_default_reviewers(repo_slug)
    print(f"✓ Default reviewers: {len(result.get('values', []))} configured")
    
    # Phase 2: Branch operations (read-only)
    print("\n[Phase 2] list_branches:")
    result = await bitbucket.list_branches(repo_slug)
    print(f"✓ Branches: {len(result.get('values', []))} found")

async def main():
    print("=" * 60)
    print("MANUAL TEST: NEW TOOLS (PHASES 1-3)")
    print("Testing with actual Atlassian connections")
    print("=" * 60)
    
    try:
        await test_jira_new_tools()
    except Exception as e:
        print(f"ERROR: Jira tests failed: {e}")
    
    try:
        await test_confluence_new_tools()
    except Exception as e:
        print(f"ERROR: Confluence tests failed: {e}")
    
    try:
        await test_bitbucket_new_tools()
    except Exception as e:
        print(f"ERROR: Bitbucket tests failed: {e}")
    
    print("\n" + "=" * 60)
    print("MANUAL TESTING COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
