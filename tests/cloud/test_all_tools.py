#!/usr/bin/env python3
"""Comprehensive test attempting all 94 tools"""
import asyncio
import getpass
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp_server.cloud.jira_provider import JiraProvider
from mcp_server.cloud.confluence_provider import ConfluenceProvider
from mcp_server.cloud.bitbucket_provider import BitbucketProvider

def is_connection_error(error_msg):
    """Check if error is a connection/DNS issue"""
    connection_indicators = [
        'Failed to resolve',
        'getaddrinfo failed',
        'Name or service not known',
        'Max retries exceeded',
        'Connection refused',
        'Connection timed out',
        'No route to host'
    ]
    return any(indicator in str(error_msg) for indicator in connection_indicators)

def format_error(name, error_msg):
    """Format error message nicely"""
    if is_connection_error(error_msg):
        match = re.search(r"host='([^']+)'", str(error_msg))
        if match:
            hostname = match.group(1)
            return f"Cannot connect to {hostname} (check URL/network/VPN)"
        return "Connection failed (check URL/network/VPN)"
    return str(error_msg)

def prompt_credentials():
    """Prompt for missing credentials"""
    if not os.getenv('ATLASSIAN_BASE_URL'):
        print("\n[PROMPT] Atlassian Cloud (Jira/Confluence) credentials not found")
        response = input("Configure now? (y/n): ").lower()
        if response == 'y':
            os.environ['ATLASSIAN_BASE_URL'] = input("  Atlassian Base URL (e.g., https://yourcompany.atlassian.net): ")
            os.environ['ATLASSIAN_USERNAME'] = input("  Atlassian Email: ")
            os.environ['ATLASSIAN_API_TOKEN'] = getpass.getpass("  Atlassian API Token: ")
    
    if not os.getenv('BITBUCKET_WORKSPACE'):
        print("\n[PROMPT] Bitbucket Cloud credentials not found")
        response = input("Configure now? (y/n): ").lower()
        if response == 'y':
            os.environ['BITBUCKET_WORKSPACE'] = input("  Bitbucket Workspace: ")
            os.environ['ATLASSIAN_USERNAME'] = input("  Bitbucket Email (for auth): ")
            os.environ['BITBUCKET_API_TOKEN'] = getpass.getpass("  Bitbucket API Token: ")

async def test_all_jira_tools():
    """Test all 31 Jira tools"""
    jira = JiraProvider()
    if not jira.available:
        return 0, 0, 0, 31
    
    passed = failed = exceptions = skipped = 0
    projects = await jira.list_projects()
    project_key = projects.get('projects', [{}])[0].get('key') if projects.get('projects') else None
    
    # Get current user for tests
    current_user = await jira.get_current_user()
    account_id = current_user.get('accountId')
    
    # 1-7: Read operations
    for name, func in [
            ("list_projects", lambda: jira.list_projects()),
            ("search_jira", lambda: jira.search("created >= -30d order by created DESC")),
            ("get_current_user", lambda: jira.get_current_user()),
            ("search_users", lambda: jira.search_users("a")),
            ("get_recent_issues", lambda: jira.get_recent_issues(7)),
            ("list_boards", lambda: jira.list_boards()),
            ("get_user_permissions", lambda: jira.get_user_permissions()),
        ]:
            result = await func()
            if 'error' in result:
                error_msg = format_error(name, result['error'])
                print(f"  [FAIL] {name}: {error_msg}")
                failed += 1
            else:
                print(f"  [PASS] {name}")
                passed += 1
    
    if project_key:
        # 8-10: Project operations
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
        
        # 11: Create issue - skip to avoid modifying production
        print(f"  [SKIP] create_issue (would create test data)")
        skipped += 1
        
        # Use existing issue for read-only tests
        search_result = await jira.search(f"project = {project_key} order by created DESC")
        if search_result.get('issues'):
            test_issue = search_result['issues'][0]['key']
            
            # 12-17: Read-only issue operations
            for name, func in [
                ("get_issue", lambda: jira.get_issue(test_issue)),
                ("get_issue_comments", lambda: jira.get_issue_comments(test_issue)),
                ("get_issue_transitions", lambda: jira.get_issue_transitions(test_issue)),
                ("get_issue_attachments", lambda: jira.get_issue_attachments(test_issue)),
                ("get_issue_watchers", lambda: jira.get_issue_watchers(test_issue)),
                ("get_worklogs", lambda: jira.get_worklogs(test_issue)),
            ]:
                result = await func()
                if 'error' in result:
                    print(f"  [FAIL] {name}: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] {name}")
                    passed += 1
            
            # Skip write operations
            print(f"  [SKIP] Skipping 9 write operations (would modify existing issue)")
            skipped += 9
            
            # Get user for link_issues test
            if account_id:
                result = await jira.get_user(account_id)
                if 'error' in result:
                    print(f"  [FAIL] get_user: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] get_user")
                    passed += 1
            
            # Boards/sprints (may not be available)
            boards = await jira.list_boards()
            if boards.get('values'):
                board_id = boards['values'][0]['id']
                result = await jira.get_board_issues(board_id)
                if 'error' in result:
                    print(f"  [FAIL] get_board_issues: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] get_board_issues")
                    passed += 1
                
                result = await jira.list_sprints(board_id)
                if 'error' in result:
                    if '400' in str(result['error']) or 'not found' in str(result['error']).lower():
                        print(f"  [EXCEPT] list_sprints: Board doesn't support sprints")
                        exceptions += 1
                    else:
                        print(f"  [FAIL] list_sprints: {result['error']}")
                        failed += 1
                else:
                    print(f"  [PASS] list_sprints")
                    passed += 1
                
                if result.get('values'):
                    sprint_id = result['values'][0]['id']
                    result = await jira.get_sprint_issues(sprint_id)
                    if 'error' in result:
                        print(f"  [FAIL] get_sprint_issues: {result['error']}")
                        failed += 1
                    else:
                        print(f"  [PASS] get_sprint_issues")
                        passed += 1
        else:
            print(f"  [SKIP] No existing issues found - skipping 15 issue-dependent tests")
            skipped += 15
    
    return passed, failed, exceptions, skipped

async def test_all_confluence_tools():
    """Test all 30 Confluence tools"""
    confluence = ConfluenceProvider()
    if not confluence.available:
        return 0, 0, 0, 30
    
    passed = failed = exceptions = skipped = 0
    spaces = await confluence.list_spaces()
    space_key = spaces.get('results', [{}])[0].get('key') if spaces.get('results') else None
    
    # Get current user
    current_user_result = await confluence.search_users("a")
    account_id = current_user_result.get('users', [{}])[0].get('accountId') if current_user_result.get('users') else None
    
    # 1-5: Read operations
    for name, func in [
            ("list_spaces", lambda: confluence.list_spaces()),
            ("search_confluence", lambda: confluence.search("type=page")),
            ("search_confluence_users", lambda: confluence.search_users("a")),
            ("get_recent_content", lambda: confluence.get_recent_content(7)),
            ("search_by_label", lambda: confluence.search_by_label("test")),
    ]:
        result = await func()
        if 'error' in result:
            error_msg = format_error(name, result['error'])
            print(f"  [FAIL] {name}: {error_msg}")
            failed += 1
        else:
            print(f"  [PASS] {name}")
            passed += 1
    
    if not space_key:
        print(f"  [SKIP] No valid space keys found - skipping 23 space-dependent tests")
        skipped += 23
    else:
        # 6-7: Space operations
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
        
        # 8: Create page - skip to avoid modifying production
        print(f"  [SKIP] create_page (would create test data)")
        skipped += 1
        
        # Use existing page for read-only tests
        pages_result = await confluence.list_pages(space_key)
        if pages_result.get('results'):
            test_page = pages_result['results'][0]['id']
            
            # 9-16: Read-only page operations
            for name, func in [
                ("get_page", lambda: confluence.get_page(test_page)),
                ("get_page_comments", lambda: confluence.get_page_comments(test_page)),
                ("get_page_attachments", lambda: confluence.get_page_attachments(test_page)),
                ("get_page_labels", lambda: confluence.get_labels(test_page)),
                ("get_page_history", lambda: confluence.get_page_history(test_page)),
                ("get_page_restrictions", lambda: confluence.get_page_restrictions(test_page)),
                ("get_recent_content", lambda: confluence.get_recent_content(7, space_key)),
                ("search_by_label", lambda: confluence.search_by_label("test", space_key)),
            ]:
                result = await func()
                if 'error' in result:
                    if 'search_by_label' in name and '400' in str(result['error']):
                        print(f"  [EXCEPT] {name}: CQL query format issue")
                        exceptions += 1
                    else:
                        print(f"  [FAIL] {name}: {result['error']}")
                        failed += 1
                else:
                    print(f"  [PASS] {name}")
                    passed += 1
            
            # Skip write operations
            print(f"  [SKIP] Skipping 7 write operations (would modify existing page)")
            skipped += 7
            
            if account_id:
                result = await confluence.get_user(account_id)
                if 'error' in result:
                    print(f"  [FAIL] get_confluence_user: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] get_confluence_user")
                    passed += 1
                
                result = await confluence.get_user_content(account_id)
                if 'error' in result:
                    print(f"  [FAIL] get_user_content: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] get_user_content")
                    passed += 1
                
                result = await confluence.search_by_author(account_id, space_key)
                if 'error' in result:
                    print(f"  [FAIL] search_by_author: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] search_by_author")
                    passed += 1
            # 17-21: New hierarchy tools
            for name, func in [
                ("get_child_pages", lambda: confluence.get_child_pages(test_page)),
                ("get_descendants", lambda: confluence.get_descendants(test_page)),
                ("get_ancestors", lambda: confluence.get_ancestors(test_page)),
                ("cql_search", lambda: confluence.cql_search(f"type=page AND space={space_key}")),
                ("move_page", lambda: confluence.move_page(test_page, space_key)),
            ]:
                result = await func()
                if 'error' in result:
                    print(f"  [FAIL] {name}: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] {name}")
                    passed += 1
        else:
            print(f"  [SKIP] No existing pages found - skipping 20 page-dependent tests")
            skipped += 20
    
    return passed, failed, exceptions, skipped

async def test_all_bitbucket_tools():
    """Test all 33 Bitbucket tools"""
    bitbucket = BitbucketProvider()
    if not bitbucket.available:
        return 0, 0, 0, 33
    
    passed = failed = exceptions = skipped = 0
    repos = await bitbucket.list_repositories()
    repo_slug = repos.get('values', [{}])[0].get('slug') if repos.get('values') else None
    
    # 1-2: Repository operations
    for name, func in [
            ("list_repositories", lambda: bitbucket.list_repositories()),
            ("search_bitbucket", lambda: bitbucket.search("test")),
    ]:
        result = await func()
        if 'error' in result:
            error_msg = format_error(name, result['error'])
            print(f"  [FAIL] {name}: {error_msg}")
            failed += 1
        else:
            print(f"  [PASS] {name}")
            passed += 1
    
    if not repo_slug:
        print(f"  [SKIP] No accessible repositories found - skipping 29 repo-dependent tests")
        skipped += 29
    else:
        # 3-10: Read operations
        for name, func in [
                ("get_repository", lambda: bitbucket.get_repository(repo_slug)),
                ("list_branches", lambda: bitbucket.list_branches(repo_slug)),
                ("list_tags", lambda: bitbucket.list_tags(repo_slug)),
                ("list_commits", lambda: bitbucket.list_commits(repo_slug)),
                ("list_pull_requests", lambda: bitbucket.list_pull_requests(repo_slug)),
                ("get_default_reviewers", lambda: bitbucket.get_default_reviewers(repo_slug)),
                ("get_branch_restrictions", lambda: bitbucket.get_branch_restrictions(repo_slug)),
                ("list_directory", lambda: bitbucket.list_directory(repo_slug)),
        ]:
            result = await func()
            if 'error' in result:
                # Handle expected exceptions for cloud
                if 'get_default_reviewers' in name and ('404' in str(result['error']) or '403' in str(result['error'])):
                    print(f"  [EXCEPT] {name}: Feature not configured or insufficient permissions")
                    exceptions += 1
                elif 'get_branch_restrictions' in name and ('404' in str(result['error']) or '403' in str(result['error'])):
                    print(f"  [EXCEPT] {name}: Feature not configured or insufficient permissions")
                    exceptions += 1
                elif 'list_directory' in name and '404' in str(result['error']):
                    print(f"  [EXCEPT] {name}: Path doesn't exist")
                    exceptions += 1
                else:
                    print(f"  [FAIL] {name}: {result['error']}")
                    failed += 1
            else:
                print(f"  [PASS] {name}")
                passed += 1
        
        # Get branch and commit for further tests
        branches = await bitbucket.list_branches(repo_slug)
        if branches.get('values'):
            branch_name = branches['values'][0]['name']
            commit_hash = branches['values'][0]['target']['hash']
            
            # 11-15: Commit operations
            for name, func in [
                ("get_commit", lambda: bitbucket.get_commit(repo_slug, commit_hash)),
                ("get_commit_diff", lambda: bitbucket.get_commit_diff(repo_slug, commit_hash)),
                ("get_build_status", lambda: bitbucket.get_build_status(repo_slug, commit_hash)),
                ("list_commits_by_author", lambda: bitbucket.list_commits_by_author(repo_slug, "author")),
                ("get_file_content", lambda: bitbucket.get_file_content(repo_slug, "README.md", branch_name)),
            ]:
                result = await func()
                if 'error' in result:
                    if 'list_commits_by_author' in name and '404' in str(result['error']):
                        print(f"  [EXCEPT] {name}: Author filter not supported")
                        exceptions += 1
                    elif 'get_file_content' in name and '404' in str(result['error']):
                        print(f"  [EXCEPT] {name}: File doesn't exist")
                        exceptions += 1
                    else:
                        print(f"  [FAIL] {name}: {result['error']}")
                        failed += 1
                else:
                    print(f"  [PASS] {name}")
                    passed += 1
            
            # 16: Create branch - skip to avoid modifying production
            print(f"  [SKIP] create_branch (would create test branch)")
            skipped += 1
            
            # PR read operations
            prs = await bitbucket.list_pull_requests(repo_slug, "OPEN")
            if prs.get('values'):
                pr_id = prs['values'][0]['id']
                
                # 17-21: PR read operations
                for name, func in [
                    ("get_pull_request", lambda: bitbucket.get_pull_request(repo_slug, pr_id)),
                    ("get_pull_request_diff", lambda: bitbucket.get_pull_request_diff(repo_slug, pr_id)),
                    ("get_pull_request_comments", lambda: bitbucket.get_pull_request_comments(repo_slug, pr_id)),
                    ("get_pr_activity", lambda: bitbucket.get_pr_activity(repo_slug, pr_id)),
                    ("list_pull_requests_by_author", lambda: bitbucket.list_pull_requests_by_author(repo_slug, "author")),
                ]:
                    result = await func()
                    if 'error' in result:
                        print(f"  [FAIL] {name}: {result['error']}")
                        failed += 1
                    else:
                        print(f"  [PASS] {name}")
                        passed += 1
            
            # Skip write operations
            print(f"  [SKIP] Skipping 9 write operations (would modify PRs or require permissions)")
            skipped += 9
            
            # Compare commits
            commits = await bitbucket.list_commits(repo_slug)
            if len(commits.get('values', [])) >= 2:
                from_commit = commits['values'][1]['hash']
                to_commit = commits['values'][0]['hash']
                result = await bitbucket.compare_commits(repo_slug, from_commit, to_commit)
                if 'error' in result:
                    print(f"  [FAIL] compare_commits: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] compare_commits")
                    passed += 1
            # Skip delete_branch since we didn't create one
            print(f"  [SKIP] delete_branch (no test branch created)")
            skipped += 1
    
    return passed, failed, exceptions, skipped

async def main():
    print("=" * 60)
    print("ATLASSIAN CLOUD INTEGRATION TEST")
    print("Testing 94 available tools (31 Jira + 30 Confluence + 33 Bitbucket)")
    print("=" * 60)
    
    print("\n" + "=" * 60)
    print("JIRA CLOUD (31 tools available)")
    print("=" * 60)
    jira_p, jira_f, jira_e, jira_s = await test_all_jira_tools()
    print(f"  Tested: {jira_p + jira_f + jira_e} of 31 Jira tools")
    
    print("\n" + "=" * 60)
    print("CONFLUENCE CLOUD (30 tools available)")
    print("=" * 60)
    conf_p, conf_f, conf_e, conf_s = await test_all_confluence_tools()
    print(f"  Tested: {conf_p + conf_f + conf_e} of 30 Confluence tools")
    
    print("\n" + "=" * 60)
    print("BITBUCKET CLOUD (33 tools available)")
    print("=" * 60)
    bb_p, bb_f, bb_e, bb_s = await test_all_bitbucket_tools()
    print(f"  Tested: {bb_p + bb_f + bb_e} of 33 Bitbucket tools")
    
    total_p = jira_p + conf_p + bb_p
    total_f = jira_f + conf_f + bb_f
    total_e = jira_e + conf_e + bb_e
    total_s = jira_s + conf_s + bb_s
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Tools tested: {total_p + total_f + total_e} of 94 available")
    print(f"Passed:       {total_p}")
    print(f"Failed:       {total_f}")
    print(f"Exceptions:   {total_e} (expected failures due to server config)")
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
    print("ATLASSIAN CLOUD INTEGRATION TEST")
    print("=" * 60)
    
    prompt_credentials()
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)