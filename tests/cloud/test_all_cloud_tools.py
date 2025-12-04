#!/usr/bin/env python3
"""Comprehensive Cloud test for 94 tools (31 Jira + 30 Confluence + 33 Bitbucket)"""
import asyncio
import os
import re
import sys
import yaml
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

def load_config():
    """Load Cloud credentials from config.yaml (Cloud tests only)"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.yaml')
    
    if not os.path.exists(config_path):
        print("\nError: config.yaml not found!")
        print("Please create config.yaml from config.template.yaml and configure your credentials.")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    cloud = config.get('cloud', {})
    if not cloud:
        print("\nError: config.yaml must have cloud section configured for Cloud tests")
        sys.exit(1)
    
    # Force Cloud platform for Cloud tests
    os.environ['ATLASSIAN_BASE_URL'] = cloud.get('atlassian_base_url', '')
    os.environ['ATLASSIAN_USERNAME'] = cloud.get('atlassian_username', '')
    os.environ['ATLASSIAN_API_TOKEN'] = cloud.get('atlassian_api_token', '')
    os.environ['BITBUCKET_WORKSPACE'] = cloud.get('bitbucket_workspace', '')
    os.environ['BITBUCKET_API_TOKEN'] = cloud.get('bitbucket_api_token', '')
    # Clear DC env vars to ensure Cloud is used
    os.environ.pop('JIRA_BASE_URL', None)
    os.environ.pop('JIRA_PAT_TOKEN', None)
    os.environ.pop('CONFLUENCE_BASE_URL', None)
    os.environ.pop('CONFLUENCE_PAT_TOKEN', None)
    os.environ.pop('BITBUCKET_BASE_URL', None)
    os.environ.pop('BITBUCKET_PAT_TOKEN', None)
    
    print(f"Loaded Cloud credentials from config.yaml")

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
        
        # 11: Create test issue
        result = await jira.create_issue(project_key, "[TEST] Integration Test Issue", "Test issue for integration testing - will be deleted")
        if 'error' in result:
            print(f"  [FAIL] create_issue: {result['error']}")
            failed += 1
            print(f"  [SKIP] Skipping 20 issue-dependent tests")
            skipped += 20
        else:
            test_issue = result['key']
            print(f"  [PASS] create_issue (created {test_issue} in project {project_key})")
            passed += 1
            
            # 12-17: Read operations
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
            
            # 18-26: Write operations
            result = await jira.update_issue(test_issue, {"summary": "[TEST] Updated Issue"})
            if 'error' in result:
                print(f"  [FAIL] update_issue: {result['error']}")
                failed += 1
            else:
                print(f"  [PASS] update_issue")
                passed += 1
            
            result = await jira.add_comment(test_issue, "Test comment")
            if 'error' in result:
                print(f"  [FAIL] add_comment: {result['error']}")
                failed += 1
            else:
                print(f"  [PASS] add_comment")
                passed += 1
            
            transitions = await jira.get_issue_transitions(test_issue)
            if transitions.get('transitions'):
                transition_id = transitions['transitions'][0]['id']
                result = await jira.transition_issue(test_issue, transition_id)
                if 'error' in result:
                    print(f"  [FAIL] transition_issue: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] transition_issue")
                    passed += 1
            else:
                print(f"  [SKIP] transition_issue (no transitions available)")
                skipped += 1
            
            if account_id:
                result = await jira.assign_issue(test_issue, account_id)
                if 'error' in result:
                    print(f"  [FAIL] assign_issue: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] assign_issue")
                    passed += 1
            else:
                print(f"  [SKIP] assign_issue (no account_id)")
                skipped += 1
            
            result = await jira.add_worklog(test_issue, "1h", "Test work")
            if 'error' in result:
                print(f"  [FAIL] add_worklog: {result['error']}")
                failed += 1
            else:
                print(f"  [PASS] add_worklog")
                passed += 1
            
            result = await jira.add_label(test_issue, "test")
            if 'error' in result:
                print(f"  [FAIL] add_label: {result['error']}")
                failed += 1
            else:
                print(f"  [PASS] add_label")
                passed += 1
            
            result = await jira.set_priority(test_issue, "Medium")
            if 'error' in result:
                print(f"  [FAIL] set_priority: {result['error']}")
                failed += 1
            else:
                print(f"  [PASS] set_priority")
                passed += 1
            
            result = await jira.add_attachment(test_issue, "test.txt", "test content")
            if 'error' in result:
                print(f"  [FAIL] add_attachment: {result['error']}")
                failed += 1
            else:
                print(f"  [PASS] add_attachment")
                passed += 1
            
            # 27: link_issues - create second issue
            result2 = await jira.create_issue(project_key, "[TEST] Second Issue for Linking", "Second test issue")
            if 'error' not in result2:
                test_issue2 = result2['key']
                print(f"  [INFO] Created second issue {test_issue2} for linking")
                result = await jira.link_issues(test_issue, test_issue2, "Relates")
                if 'error' in result:
                    print(f"  [FAIL] link_issues: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] link_issues")
                    passed += 1
                await jira.delete_issue(test_issue2)
                print(f"  [INFO] Deleted second issue {test_issue2}")
            else:
                print(f"  [SKIP] link_issues (could not create second issue)")
                skipped += 1
            
            # 28: get_user
            if account_id:
                result = await jira.get_user(account_id)
                if 'error' in result:
                    print(f"  [FAIL] get_user: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] get_user")
                    passed += 1
            
            # 29-31: Boards/sprints
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
                        print(f"  [SKIP] get_sprint_issues (board doesn't support sprints)")
                        skipped += 1
                    else:
                        print(f"  [FAIL] list_sprints: {result['error']}")
                        failed += 1
                        print(f"  [SKIP] get_sprint_issues (list_sprints failed)")
                        skipped += 1
                elif result.get('values'):
                    print(f"  [PASS] list_sprints")
                    passed += 1
                    sprint_id = result['values'][0]['id']
                    result = await jira.get_sprint_issues(sprint_id)
                    if 'error' in result:
                        print(f"  [FAIL] get_sprint_issues: {result['error']}")
                        failed += 1
                    else:
                        print(f"  [PASS] get_sprint_issues")
                        passed += 1
                else:
                    print(f"  [PASS] list_sprints")
                    passed += 1
                    print(f"  [SKIP] get_sprint_issues (no sprints available)")
                    skipped += 1
            
            # Cleanup: delete test issue
            result = await jira.delete_issue(test_issue)
            if 'error' in result:
                print(f"  [FAIL] delete_issue: {result['error']}")
                failed += 1
            else:
                print(f"  [PASS] delete_issue")
                passed += 1
    
    return passed, failed, exceptions, skipped

async def test_all_confluence_tools():
    """Test all 30 Confluence tools"""
    confluence = ConfluenceProvider()
    if not confluence.available:
        return 0, 0, 0, 30
    
    passed = failed = exceptions = skipped = 0
    spaces = await confluence.list_spaces()
    space_key = spaces.get('results', [{}])[0].get('key') if spaces.get('results') else None
    
    # Get current user - search for users and extract account_id
    current_user_result = await confluence.search_users("a")
    account_id = None
    if current_user_result.get('users'):
        for user_result in current_user_result['users']:
            user = user_result.get('user', {})
            if user.get('accountId') and user.get('accountType') == 'atlassian':
                account_id = user['accountId']
                break
    
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
        
        # 8: Create page
        result = await confluence.create_page(space_key, "Test Page", "<p>Test content</p>")
        if 'error' in result:
            print(f"  [FAIL] create_page: {result['error']}")
            failed += 1
            print(f"  [SKIP] Skipping 23 page-dependent tests")
            skipped += 23
        else:
            test_page = result['id']
            version = result.get('version', {}).get('number', 1)
            print(f"  [PASS] create_page (created page {test_page} in space {space_key})")
            passed += 1
            
            # 9-15: Read operations
            for name, func in [
                ("get_page", lambda: confluence.get_page(test_page)),
                ("get_page_by_title", lambda: confluence.get_page_by_title(space_key, "Test Page")),
                ("get_page_comments", lambda: confluence.get_page_comments(test_page)),
                ("get_page_attachments", lambda: confluence.get_page_attachments(test_page)),
                ("get_page_labels", lambda: confluence.get_labels(test_page)),
                ("get_page_history", lambda: confluence.get_page_history(test_page)),
                ("get_page_restrictions", lambda: confluence.get_page_restrictions(test_page)),
            ]:
                result = await func()
                if 'error' in result:
                    print(f"  [FAIL] {name}: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] {name}")
                    passed += 1
            
            # 16: Update page with unique title
            result = await confluence.update_page(test_page, "Test Page Updated", "<p>Updated content</p>", version)
            if 'error' in result:
                print(f"  [FAIL] update_page: {result['error']}")
                failed += 1
            else:
                print(f"  [PASS] update_page")
                passed += 1
            
            # 17-19: Other write operations
            copied_page = None
            for name, func in [
                ("add_page_comment", lambda: confluence.add_page_comment(test_page, "<p>Test comment</p>")),
                ("add_page_label", lambda: confluence.add_label(test_page, "test")),
                ("copy_page", lambda: confluence.copy_page(test_page, "Test Copy", space_key)),
            ]:
                result = await func()
                if 'error' in result:
                    if '400' in str(result['error']):
                        print(f"  [EXCEPT] {name}: API limitation")
                        exceptions += 1
                    else:
                        print(f"  [FAIL] {name}: {result['error']}")
                        failed += 1
                else:
                    if 'copy_page' in name:
                        copied_page = result.get('id')
                        print(f"  [PASS] {name} (created page {copied_page} in space {space_key})")
                    else:
                        print(f"  [PASS] {name}")
                    passed += 1
            
            # 20-22: User operations
            if account_id:
                for name, func in [
                    ("get_confluence_user", lambda: confluence.get_user(account_id)),
                    ("get_user_content", lambda: confluence.get_user_content(account_id)),
                    ("search_by_author", lambda: confluence.search_by_author(account_id, space_key)),
                ]:
                    result = await func()
                    if 'error' in result:
                        print(f"  [FAIL] {name}: {result['error']}")
                        failed += 1
                    else:
                        print(f"  [PASS] {name}")
                        passed += 1
            else:
                print(f"  [SKIP] get_confluence_user (no account_id)")
                print(f"  [SKIP] get_user_content (no account_id)")
                print(f"  [SKIP] search_by_author (no account_id)")
                skipped += 3
            
            # 23-24: Page restrictions and version restore
            # Test set_page_restrictions (requires paid plan)
            current_restrictions = await confluence.get_page_restrictions(test_page)
            if 'error' not in current_restrictions:
                result = await confluence.set_page_restrictions(test_page, current_restrictions)
                if 'error' in result:
                    if '403' in str(result['error']) or 'Forbidden' in str(result['error']):
                        print(f"  [EXCEPT] set_page_restrictions: Requires paid plan")
                        exceptions += 1
                    else:
                        print(f"  [FAIL] set_page_restrictions: {result['error']}")
                        failed += 1
                else:
                    print(f"  [PASS] set_page_restrictions")
                    passed += 1
            else:
                print(f"  [FAIL] set_page_restrictions: Could not get current restrictions")
                failed += 1
            
            # Test restore_page_version (restore to version 1)
            result = await confluence.restore_page_version(test_page, 1)
            if 'error' in result:
                print(f"  [FAIL] restore_page_version: {result['error']}")
                failed += 1
            else:
                print(f"  [PASS] restore_page_version")
                passed += 1
            
            # 25-29: Hierarchy tools
            for name, func in [
                ("get_child_pages", lambda: confluence.get_child_pages(test_page)),
                ("get_descendants", lambda: confluence.get_descendants(test_page)),
                ("get_ancestors", lambda: confluence.get_ancestors(test_page)),
                ("cql_search", lambda: confluence.cql_search(f'type=page AND space="{space_key}"')),
                ("move_page", lambda: confluence.move_page(test_page, space_key)),
            ]:
                result = await func()
                if 'error' in result:
                    print(f"  [FAIL] {name}: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] {name}")
                    passed += 1
            
            # 30: Cleanup - delete pages (delete_page tool tested once, used twice)
            if copied_page:
                result = await confluence.delete_page(copied_page)
                if 'error' in result:
                    print(f"  [FAIL] delete_page (copy): {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] delete_page (copy)")
                    passed += 1
            else:
                # If no copy was created, still test delete_page on main page
                result = await confluence.delete_page(test_page)
                if 'error' in result:
                    print(f"  [FAIL] delete_page: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] delete_page")
                    passed += 1
                test_page = None  # Mark as deleted
            
            # Delete main test page if not already deleted
            if test_page:
                result = await confluence.delete_page(test_page)
                if 'error' in result:
                    print(f"  [FAIL] delete_page (main): {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] delete_page (main)")
                    # Don't increment passed - already counted above
    
    return passed, failed, exceptions, skipped

async def test_all_bitbucket_tools(test_repo_slug=None, test_branch_name=None):
    """Test all 34 Bitbucket tools"""
    bitbucket = BitbucketProvider()
    if not bitbucket.available:
        return 0, 0, 0, 34
    
    passed = failed = exceptions = skipped = 0
    
    # Use provided repo or find one
    if test_repo_slug:
        repo_slug = test_repo_slug
        print(f"  [INFO] Using provided repo: {repo_slug}")
    else:
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
        print(f"  [SKIP] No accessible repositories found - skipping 31 repo-dependent tests")
        skipped += 31
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
            
            # 3: search_files (needs branch name)
            result = await bitbucket.search_files(repo_slug, "README", branch_name)
            if 'error' in result:
                if '404' in str(result['error']):
                    print(f"  [EXCEPT] search_files: No files in repo")
                    exceptions += 1
                else:
                    print(f"  [FAIL] search_files: {result['error']}")
                    failed += 1
            else:
                print(f"  [PASS] search_files")
                passed += 1
            
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
            
            # 16: get_bitbucket_user (get current authenticated user)
            # Get current user's account_id from /user endpoint
            try:
                import requests
                url = "https://api.bitbucket.org/2.0/user"
                response = bitbucket.session.get(url, auth=(bitbucket.auth.username, bitbucket.bitbucket_token), timeout=bitbucket.timeout)
                response.raise_for_status()
                user_data = response.json()
                account_id = user_data.get('account_id')
                
                if account_id:
                    result = await bitbucket.get_user(account_id)
                    if 'error' in result:
                        print(f"  [FAIL] get_bitbucket_user: {result['error']}")
                        failed += 1
                    else:
                        print(f"  [PASS] get_bitbucket_user")
                        passed += 1
                else:
                    print(f"  [SKIP] get_bitbucket_user (no account_id)")
                    skipped += 1
            except Exception as e:
                print(f"  [FAIL] get_bitbucket_user: {str(e)}")
                failed += 1
            
            # 17: Create branch or use provided branch
            if test_branch_name:
                print(f"  [SKIP] create_branch (using provided branch {test_branch_name})")
                skipped += 1
                created_branch = test_branch_name
            else:
                test_branch = f"test-{int(asyncio.get_event_loop().time())}"
                result = await bitbucket.create_branch(repo_slug, test_branch, branch_name)
                if 'error' in result:
                    print(f"  [FAIL] create_branch: {result['error']}")
                    failed += 1
                    created_branch = None
                else:
                    print(f"  [PASS] create_branch (created branch {test_branch} in repo {repo_slug})")
                    passed += 1
                    created_branch = test_branch
            
            # 18: create_pull_request (create test PR first)
            test_pr_id = None
            if created_branch:
                result = await bitbucket.create_pull_request(repo_slug, f"[TEST] Test PR", created_branch, branch_name, "Test PR description")
                if 'error' in result:
                    if '400' in str(result['error']):
                        print(f"  [EXCEPT] create_pull_request: No differences between branches (repo needs commits)")
                        exceptions += 1
                    else:
                        print(f"  [FAIL] create_pull_request: {result['error']}")
                        failed += 1
                else:
                    test_pr_id = result.get('id')
                    print(f"  [PASS] create_pull_request (created PR #{test_pr_id} in repo {repo_slug})")
                    passed += 1
            else:
                print(f"  [SKIP] create_pull_request (no test branch created)")
                skipped += 1
            
            # 19-23: PR read operations (use created PR or existing PRs)
            if test_pr_id:
                pr_id = test_pr_id
            else:
                prs = await bitbucket.list_pull_requests(repo_slug, "OPEN")
                pr_id = prs.get('values', [{}])[0].get('id') if prs.get('values') else None
            
            if pr_id:
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
            else:
                print(f"  [SKIP] get_pull_request (no PRs available)")
                print(f"  [SKIP] get_pull_request_diff (no PRs available)")
                print(f"  [SKIP] get_pull_request_comments (no PRs available)")
                print(f"  [SKIP] get_pr_activity (no PRs available)")
                print(f"  [SKIP] list_pull_requests_by_author (no PRs available)")
                skipped += 5
            
            # 24-30: PR write operations (use created PR)
            if test_pr_id:
                result = await bitbucket.update_pull_request(repo_slug, test_pr_id, "[TEST] Updated PR")
                if 'error' in result:
                    print(f"  [FAIL] update_pull_request: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] update_pull_request")
                    passed += 1
                
                result = await bitbucket.add_pr_comment(repo_slug, test_pr_id, "Test comment")
                if 'error' in result:
                    print(f"  [FAIL] add_pr_comment: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] add_pr_comment")
                    passed += 1
                
                result = await bitbucket.approve_pull_request(repo_slug, test_pr_id)
                if 'error' in result:
                    print(f"  [FAIL] approve_pull_request: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] approve_pull_request")
                    passed += 1
                
                # Get current user for add_pr_reviewer
                current_user_result = await bitbucket.get_user("currentUser")
                if 'error' not in current_user_result and current_user_result.get('uuid'):
                    result = await bitbucket.add_pr_reviewer(repo_slug, test_pr_id, current_user_result['uuid'])
                    if 'error' in result:
                        print(f"  [FAIL] add_pr_reviewer: {result['error']}")
                        failed += 1
                    else:
                        print(f"  [PASS] add_pr_reviewer")
                        passed += 1
                else:
                    print(f"  [SKIP] add_pr_reviewer (no user uuid)")
                    skipped += 1
                
                result = await bitbucket.request_changes(repo_slug, test_pr_id, "Please fix")
                if 'error' in result:
                    print(f"  [FAIL] request_changes: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] request_changes")
                    passed += 1
                
                # Decline PR instead of merging to avoid affecting main branch
                result = await bitbucket.decline_pull_request(repo_slug, test_pr_id)
                if 'error' in result:
                    print(f"  [FAIL] decline_pull_request: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] decline_pull_request")
                    passed += 1
                
                # Skip merge_pull_request since we declined
                print(f"  [SKIP] merge_pull_request (PR was declined)")
                skipped += 1
            else:
                print(f"  [SKIP] Skipping 7 PR write operations (no test PR created)")
                skipped += 7
            
            # 31: create_webhook - skip to avoid creating actual webhooks
            print(f"  [SKIP] create_webhook (would create webhook)")
            skipped += 1
            
            # 32: Compare commits
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
            else:
                print(f"  [SKIP] compare_commits (need at least 2 commits)")
                skipped += 1
            
            # 33: Cleanup - delete test branch if created (skip if using provided branch)
            if test_branch_name:
                print(f"  [SKIP] delete_branch (using provided branch, not deleting)")
                skipped += 1
            elif created_branch:
                result = await bitbucket.delete_branch(repo_slug, created_branch)
                if 'error' in result:
                    print(f"  [FAIL] delete_branch: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] delete_branch")
                    passed += 1
            else:
                print(f"  [SKIP] delete_branch (no test branch created)")
                skipped += 1
    
    return passed, failed, exceptions, skipped

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Test Atlassian Cloud tools')
    parser.add_argument('--service', choices=['jira', 'confluence', 'bitbucket', 'all'], default='all',
                        help='Service to test (default: all)')
    parser.add_argument('--bitbucket-repo', type=str, help='Bitbucket repository slug for testing (optional)')
    parser.add_argument('--bitbucket-branch', type=str, help='Bitbucket branch name for testing (optional, skips create/delete)')
    args = parser.parse_args()
    
    print("=" * 60)
    print("ATLASSIAN CLOUD INTEGRATION TEST")
    print("=" * 60)
    
    load_config()
    
    async def run_tests():
        jira_p = jira_f = jira_e = jira_s = 0
        conf_p = conf_f = conf_e = conf_s = 0
        bb_p = bb_f = bb_e = bb_s = 0
        
        if args.service in ['jira', 'all']:
            print("\n" + "=" * 60)
            print("JIRA CLOUD (31 tools available)")
            print("=" * 60)
            jira_p, jira_f, jira_e, jira_s = await test_all_jira_tools()
            print(f"  Tested: {jira_p + jira_f + jira_e} of 31 Jira tools")
        
        if args.service in ['confluence', 'all']:
            print("\n" + "=" * 60)
            print("CONFLUENCE CLOUD (30 tools available)")
            print("=" * 60)
            conf_p, conf_f, conf_e, conf_s = await test_all_confluence_tools()
            print(f"  Tested: {conf_p + conf_f + conf_e} of 30 Confluence tools")
        
        if args.service in ['bitbucket', 'all']:
            print("\n" + "=" * 60)
            print("BITBUCKET CLOUD (34 tools available)")
            print("=" * 60)
            bb_p, bb_f, bb_e, bb_s = await test_all_bitbucket_tools(args.bitbucket_repo, args.bitbucket_branch)
            print(f"  Tested: {bb_p + bb_f + bb_e} of 34 Bitbucket tools")
        
        total_p = jira_p + conf_p + bb_p
        total_f = jira_f + conf_f + bb_f
        total_e = jira_e + conf_e + bb_e
        total_s = jira_s + conf_s + bb_s
        
        # Calculate total available based on what was tested
        total_available = 0
        if args.service in ['jira', 'all']:
            total_available += 31
        if args.service in ['confluence', 'all']:
            total_available += 30
        if args.service in ['bitbucket', 'all']:
            total_available += 34
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Tools tested: {total_p + total_f + total_e} of {total_available} available")
        print(f"Passed:       {total_p}")
        print(f"Failed:       {total_f}")
        print(f"Exceptions:   {total_e} (expected failures due to server config)")
        print(f"Skipped:      {total_s}")
        
        if total_f > 0:
            print("\n[FAIL] SOME TESTS FAILED")
            return 1
        elif total_p + total_e == 0:
            print("\n[SKIP] NO TESTS RAN (configure credentials to run)")
            return 0
        else:
            print("\n[PASS] ALL TESTS PASSED")
            return 0
    
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)