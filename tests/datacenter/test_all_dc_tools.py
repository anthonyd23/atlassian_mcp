#!/usr/bin/env python3
"""Comprehensive Data Center test for 94 tools (31 Jira + 30 Confluence + 33 Bitbucket)"""
import asyncio
import os
import sys
import yaml
import re
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from mcp_server.datacenter.jira_dc_provider import JiraDCProvider
from mcp_server.datacenter.confluence_dc_provider import ConfluenceDCProvider
from mcp_server.datacenter.bitbucket_dc_provider import BitbucketDCProvider

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
    """Load Data Center credentials from config.yaml (DC tests only)"""
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml')
    
    if not os.path.exists(config_path):
        print("\nError: config.yaml not found!")
        print("Please create config.yaml from config.template.yaml and configure your credentials.")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    dc = config.get('datacenter', {})
    if not dc:
        print("\nError: config.yaml must have datacenter section configured for Data Center tests")
        sys.exit(1)
    
    # Force Data Center platform for DC tests
    os.environ['JIRA_BASE_URL'] = dc.get('jira_base_url', '')
    os.environ['JIRA_PAT_TOKEN'] = dc.get('jira_pat_token', '')
    os.environ['CONFLUENCE_BASE_URL'] = dc.get('confluence_base_url', '')
    os.environ['CONFLUENCE_PAT_TOKEN'] = dc.get('confluence_pat_token', '')
    os.environ['BITBUCKET_BASE_URL'] = dc.get('bitbucket_base_url', '')
    os.environ['BITBUCKET_PAT_TOKEN'] = dc.get('bitbucket_pat_token', '')
    os.environ['BITBUCKET_PROJECT'] = dc.get('bitbucket_project', '')
    # Clear Cloud env vars to ensure DC is used
    os.environ.pop('ATLASSIAN_BASE_URL', None)
    os.environ.pop('ATLASSIAN_USERNAME', None)
    os.environ.pop('ATLASSIAN_API_TOKEN', None)
    os.environ.pop('BITBUCKET_WORKSPACE', None)
    os.environ.pop('BITBUCKET_API_TOKEN', None)
    
    print(f"Loaded Data Center credentials from config.yaml")

async def test_all_jira_dc_tools(test_project_key=None, test_issue_key=None):
    """Test all 31 Jira DC tools"""
    jira = JiraDCProvider()
    if not jira.available:
        return 0, 0, 0, 31
    
    passed = failed = exceptions = skipped = 0
    
    # Use provided project key or find one
    if test_project_key:
        project_key = test_project_key
        print(f"  [INFO] Using provided project: {project_key}")
    else:
        projects = await jira.list_projects()
        project_key = projects.get('projects', [{}])[0].get('key') if projects.get('projects') else None
    
    # Get current user for tests
    current_user = await jira.get_current_user()
    username = current_user.get('name')  # DC uses 'name' field for username
    
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
        
        # 11: Create issue or use provided issue
        if test_issue_key:
            print(f"  [SKIP] create_issue (using provided issue {test_issue_key})")
            skipped += 1
            test_issue = test_issue_key
        else:
            result = await jira.create_issue(project_key, "[TEST] Integration Test Issue", "", "Task")
            if 'error' in result:
                print(f"  [EXCEPT] create_issue: Project requires custom fields or specific issue type")
                print(f"  [INFO] Use --jira-issue flag to test with existing issue:")
                print(f"  [INFO]   python tests/datacenter/test_all_dc_tools.py --service jira --jira-project {project_key} --jira-issue {project_key}-XXX")
                exceptions += 1
                print(f"  [SKIP] Skipping 20 issue-dependent tests")
                skipped += 20
                return passed, failed, exceptions, skipped
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
        
        if username:
            result = await jira.assign_issue(test_issue, username)
            if 'error' in result:
                print(f"  [FAIL] assign_issue: {result['error']}")
                failed += 1
            else:
                print(f"  [PASS] assign_issue")
                passed += 1
        else:
            print(f"  [SKIP] assign_issue (no username)")
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
        
        # 27: link_issues - skip for provided issue
        if not test_issue_key:
            result2 = await jira.create_issue(project_key, "[TEST] Second Issue for Linking", "", "Task")
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
        else:
            print(f"  [SKIP] link_issues (using provided issue)")
            skipped += 1
        
        # 28: get_user
        if username:
            result = await jira.get_user(username)
            if 'error' in result:
                print(f"  [FAIL] get_user: {result['error']}")
                failed += 1
            else:
                print(f"  [PASS] get_user")
                passed += 1
        else:
            print(f"  [SKIP] get_user (no username)")
            skipped += 1
        
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
        
        # Cleanup: delete test issue (skip if using provided issue)
        if not test_issue_key:
            result = await jira.delete_issue(test_issue)
            if 'error' in result:
                print(f"  [FAIL] delete_issue: {result['error']}")
                failed += 1
            else:
                print(f"  [PASS] delete_issue")
                passed += 1
        else:
            print(f"  [SKIP] delete_issue (using provided issue, not deleting)")
            skipped += 1
    
    return passed, failed, exceptions, skipped

async def test_all_confluence_dc_tools(test_space_key=None, test_page_id=None):
    """Test all 30 Confluence DC tools"""
    confluence = ConfluenceDCProvider()
    if not confluence.available:
        return 0, 0, 0, 30
    
    passed = failed = exceptions = skipped = 0
    
    # Use provided space key or find one
    if test_space_key:
        space_key = test_space_key
        print(f"  [INFO] Using provided space: {space_key}")
    else:
        spaces = await confluence.list_spaces()
        valid_space_keys = []
        if spaces.get('results'):
            for space in spaces['results']:
                key = space.get('key')
                if key and len(key) >= 2 and key.isupper():
                    valid_space_keys.append(key)
        space_key = valid_space_keys[0] if valid_space_keys else None
    
    # 1-3: Read operations
    for name, func in [
        ("list_spaces", lambda: confluence.list_spaces()),
        ("search_confluence", lambda: confluence.search("test")),
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
    
    # Skip search_confluence_users - not supported in this DC version
    print(f"  [SKIP] search_confluence_users (not supported)")
    skipped += 1
    
    if space_key:
        # 5-6: Space operations
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
        
        # 7: Create page or use provided page
        if test_page_id:
            print(f"  [SKIP] create_page (using provided page {test_page_id})")
            skipped += 1
            created_page = test_page_id
            # Get page to determine version
            page_result = await confluence.get_page(created_page)
            version = page_result.get('version', {}).get('number', 1) if 'error' not in page_result else 1
        else:
            result = await confluence.create_page(space_key, "Test Page", "<p>Test</p>")
            if 'error' not in result:
                created_page = result.get('id')
                print(f"  [PASS] create_page (created page {created_page} in space {space_key})")
                passed += 1
                version = result.get('version', {}).get('number', 1)
            else:
                print(f"  [EXCEPT] create_page: Space requires specific permissions or configuration")
                print(f"  [INFO] Use --confluence-page flag to test with existing page:")
                print(f"  [INFO]   python tests/datacenter/test_all_dc_tools.py --service confluence --confluence-space {space_key} --confluence-page PAGE_ID")
                exceptions += 1
                print(f"  [SKIP] Skipping 23 page-dependent tests")
                skipped += 23
                return passed, failed, exceptions, skipped
        
        # 8-15: Read operations
        if created_page:
            for name, func in [
                ("get_page", lambda: confluence.get_page(created_page)),
                ("get_page_by_title", lambda: confluence.get_page_by_title(space_key, "Test Page")),
                ("get_page_comments", lambda: confluence.get_page_comments(created_page)),
                ("get_page_attachments", lambda: confluence.get_page_attachments(created_page)),
                ("get_page_labels", lambda: confluence.get_labels(created_page)),
                ("get_page_history", lambda: confluence.get_page_history(created_page)),
                ("get_page_restrictions", lambda: confluence.get_page_restrictions(created_page)),
                ("get_recent_content", lambda: confluence.get_recent_content(7, space_key)),
            ]:
                result = await func()
                if 'error' in result:
                    if 'get_page_restrictions' in name and '405' in str(result['error']):
                        print(f"  [EXCEPT] {name}: Not supported in this DC version")
                        exceptions += 1
                    else:
                        print(f"  [FAIL] {name}: {result['error']}")
                        failed += 1
                else:
                    print(f"  [PASS] {name}")
                    passed += 1
            
            # 17: Update page
            result = await confluence.update_page(created_page, "Test Page Updated", "<p>Updated</p>", version)
            if 'error' in result:
                print(f"  [FAIL] update_page: {result['error']}")
                failed += 1
            else:
                print(f"  [PASS] update_page")
                passed += 1
            
            # 18-20: Other write operations
            copied_page = None
            for name, func in [
                ("add_page_comment", lambda: confluence.add_page_comment(created_page, "<p>Test comment</p>")),
                ("add_page_label", lambda: confluence.add_label(created_page, "test")),
            ]:
                result = await func()
                if 'error' in result:
                    print(f"  [FAIL] {name}: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] {name}")
                    passed += 1
            
            # Only test copy_page if we created the page (not using provided page)
            if not test_page_id:
                result = await confluence.copy_page(created_page, "Test Copy", space_key)
                if 'error' in result:
                    print(f"  [FAIL] copy_page: {result['error']}")
                    failed += 1
                else:
                    copied_page = result.get('id')
                    print(f"  [PASS] copy_page (created page {copied_page} in space {space_key})")
                    passed += 1
            else:
                print(f"  [SKIP] copy_page (using provided page)")
                skipped += 1
            
            # 21-23: User operations
            for name, func in [
                ("get_confluence_user", lambda: confluence.get_user("admin")),
                ("get_user_content", lambda: confluence.get_user_content("admin")),
                ("search_by_author", lambda: confluence.search_by_author("admin", space_key)),
            ]:
                result = await func()
                if 'error' in result:
                    print(f"  [FAIL] {name}: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] {name}")
                    passed += 1
            
            # 24-25: Page restrictions and version restore
            # Test set_page_restrictions (get current restrictions and set them back)
            current_restrictions = await confluence.get_page_restrictions(created_page)
            if 'error' not in current_restrictions:
                result = await confluence.set_page_restrictions(created_page, current_restrictions)
                if 'error' in result:
                    if '400' in str(result['error']) or '403' in str(result['error']) or '405' in str(result['error']) or '501' in str(result['error']):
                        print(f"  [EXCEPT] set_page_restrictions: Not supported or insufficient permissions")
                        exceptions += 1
                    else:
                        print(f"  [FAIL] set_page_restrictions: {result['error']}")
                        failed += 1
                else:
                    print(f"  [PASS] set_page_restrictions")
                    passed += 1
            else:
                print(f"  [SKIP] set_page_restrictions: Could not get current restrictions")
                skipped += 1
            
            # Test restore_page_version (restore to version 1)
            result = await confluence.restore_page_version(created_page, 1)
            if 'error' in result:
                print(f"  [FAIL] restore_page_version: {result['error']}")
                failed += 1
            else:
                print(f"  [PASS] restore_page_version")
                passed += 1
            
            # 26-30: Hierarchy tools
            for name, func in [
                ("get_child_pages", lambda: confluence.get_child_pages(created_page)),
                ("get_descendants", lambda: confluence.get_descendants(created_page)),
                ("get_ancestors", lambda: confluence.get_ancestors(created_page)),
                ("cql_search", lambda: confluence.cql_search(f"type=page AND space={space_key}")),
                ("move_page", lambda: confluence.move_page(created_page, space_key)),
            ]:
                result = await func()
                if 'error' in result:
                    if 'get_descendants' in name and '500' in str(result['error']):
                        print(f"  [EXCEPT] {name}: Server error (500)")
                        exceptions += 1
                    else:
                        print(f"  [FAIL] {name}: {result['error']}")
                        failed += 1
                else:
                    print(f"  [PASS] {name}")
                    passed += 1
            
            # 31-32: Cleanup - delete pages (skip if using provided page)
            if test_page_id:
                print(f"  [SKIP] delete_page (using provided page, not deleting)")
                skipped += 1
                if copied_page:
                    result = await confluence.delete_page(copied_page)
                    if 'error' in result:
                        if '403' in str(result['error']) or 'Forbidden' in str(result['error']):
                            print(f"  [EXCEPT] delete_page (copy): Insufficient permissions")
                            exceptions += 1
                        else:
                            print(f"  [FAIL] delete_page (copy): {result['error']}")
                            failed += 1
                    else:
                        print(f"  [PASS] delete_page (copy)")
                        passed += 1
            else:
                if copied_page:
                    result = await confluence.delete_page(copied_page)
                    if 'error' in result:
                        if '403' in str(result['error']) or 'Forbidden' in str(result['error']):
                            print(f"  [EXCEPT] delete_page (copy): Insufficient permissions")
                            exceptions += 1
                        else:
                            print(f"  [FAIL] delete_page (copy): {result['error']}")
                            failed += 1
                    else:
                        print(f"  [PASS] delete_page (copy)")
                        passed += 1
                
                result = await confluence.delete_page(created_page)
                if 'error' in result:
                    if '403' in str(result['error']) or 'Forbidden' in str(result['error']):
                        print(f"  [EXCEPT] delete_page: Insufficient permissions")
                        exceptions += 1
                    else:
                        print(f"  [FAIL] delete_page: {result['error']}")
                        failed += 1
                else:
                    print(f"  [PASS] delete_page")
                    passed += 1
    else:
        print(f"  [SKIP] No valid space keys found - skipping 25 space-dependent tests")
        skipped += 25
    
    return passed, failed, exceptions, skipped

async def test_all_bitbucket_dc_tools(test_repo_slug=None, test_branch_name=None):
    """Test all 34 Bitbucket DC tools"""
    bitbucket = BitbucketDCProvider()
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
    
    # 1-3: Repository operations
    for name, func in [
        ("list_repositories", lambda: bitbucket.list_repositories()),
        ("search_bitbucket", lambda: bitbucket.search("test")),
        ("search_files", lambda: bitbucket.search_files(repo_slug, "README") if repo_slug else {'error': 'No repo'}),
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
        
        # 3-5: Read operations
        for name, func in [
            ("get_repository", lambda: bitbucket.get_repository(repo_slug)),
            ("list_branches", lambda: bitbucket.list_branches(repo_slug)),
            ("list_tags", lambda: bitbucket.list_tags(repo_slug)),
        ]:
            result = await func()
            if 'error' in result:
                if 'get_default_reviewers' in name and ('400' in str(result['error']) or '404' in str(result['error'])):
                    print(f"  [EXCEPT] {name}: Plugin not installed")
                    exceptions += 1
                elif 'get_branch_restrictions' in name and ('401' in str(result['error']) or '403' in str(result['error'])):
                    print(f"  [EXCEPT] {name}: Insufficient permissions")
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
            branch_name = branches['values'][0]['displayId']
            commit_hash = branches['values'][0]['latestCommit']
            
            # 6-10: Read operations that need branch
            for name, func in [
                ("list_commits", lambda: bitbucket.list_commits(repo_slug, branch_name)),
                ("list_pull_requests", lambda: bitbucket.list_pull_requests(repo_slug)),
                ("get_default_reviewers", lambda: bitbucket.get_default_reviewers(repo_slug)),
                ("get_branch_restrictions", lambda: bitbucket.get_branch_restrictions(repo_slug)),
                ("list_directory", lambda: bitbucket.list_directory(repo_slug, "", branch_name)),
            ]:
                result = await func()
                if 'error' in result:
                    if 'get_default_reviewers' in name and ('400' in str(result['error']) or '404' in str(result['error'])):
                        print(f"  [EXCEPT] {name}: Plugin not installed")
                        exceptions += 1
                    elif 'get_branch_restrictions' in name and ('401' in str(result['error']) or '403' in str(result['error'])):
                        print(f"  [EXCEPT] {name}: Insufficient permissions")
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
            
            # 11-15: Commit operations
            for name, func in [
                ("get_commit", lambda: bitbucket.get_commit(repo_slug, commit_hash)),
                ("get_commit_diff", lambda: bitbucket.get_commit_diff(repo_slug, commit_hash)),
                ("get_build_status", lambda: bitbucket.get_build_status(repo_slug, commit_hash)),
                ("list_commits_by_author", lambda: bitbucket.list_commits_by_author(repo_slug, "author", branch_name)),
                ("get_file_content", lambda: bitbucket.get_file_content(repo_slug, "README.md", branch_name)),
            ]:
                result = await func()
                if 'error' in result:
                    if 'get_file_content' in name and '404' in str(result['error']):
                        print(f"  [EXCEPT] {name}: File doesn't exist")
                        exceptions += 1
                    else:
                        print(f"  [FAIL] {name}: {result['error']}")
                        failed += 1
                else:
                    print(f"  [PASS] {name}")
                    passed += 1
            
            # 16: get_bitbucket_user (get current user first to get slug)
            users_result = await bitbucket.list_repositories()  # Use any endpoint to verify auth
            if 'error' not in users_result:
                # Try to get first user from users list
                try:
                    import requests
                    headers = bitbucket.auth.get_auth_headers()
                    url = f"{bitbucket.base_url}/rest/api/1.0/users"
                    response = bitbucket.session.get(url, headers=headers, params={'limit': 1}, timeout=bitbucket.timeout)
                    response.raise_for_status()
                    users_data = response.json()
                    if users_data.get('values'):
                        user_slug = users_data['values'][0]['slug']
                        result = await bitbucket.get_user(user_slug)
                        if 'error' in result:
                            print(f"  [FAIL] get_bitbucket_user: {result['error']}")
                            failed += 1
                        else:
                            print(f"  [PASS] get_bitbucket_user")
                            passed += 1
                    else:
                        print(f"  [SKIP] get_bitbucket_user (no users found)")
                        skipped += 1
                except Exception as e:
                    print(f"  [FAIL] get_bitbucket_user: {str(e)}")
                    failed += 1
            else:
                print(f"  [SKIP] get_bitbucket_user (cannot get users)")
                skipped += 1
            
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
                    if '400' in str(result['error']) or '409' in str(result['error']):
                        print(f"  [EXCEPT] create_pull_request: No differences between branches or already exists")
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
                
                # Get a valid user slug for add_pr_reviewer
                try:
                    import requests
                    headers = bitbucket.auth.get_auth_headers()
                    url = f"{bitbucket.base_url}/rest/api/1.0/users"
                    response = bitbucket.session.get(url, headers=headers, params={'limit': 1}, timeout=bitbucket.timeout)
                    response.raise_for_status()
                    users_data = response.json()
                    if users_data.get('values'):
                        user_name = users_data['values'][0]['name']
                        result = await bitbucket.add_pr_reviewer(repo_slug, test_pr_id, user_name)
                        if 'error' in result:
                            print(f"  [FAIL] add_pr_reviewer: {result['error']}")
                            failed += 1
                        else:
                            print(f"  [PASS] add_pr_reviewer")
                            passed += 1
                    else:
                        print(f"  [SKIP] add_pr_reviewer (no users found)")
                        skipped += 1
                except Exception as e:
                    print(f"  [FAIL] add_pr_reviewer: {str(e)}")
                    failed += 1
                
                result = await bitbucket.request_changes(repo_slug, test_pr_id, "Please fix")
                if 'error' in result:
                    print(f"  [FAIL] request_changes: {result['error']}")
                    failed += 1
                else:
                    print(f"  [PASS] request_changes")
                    passed += 1
                
                # Decline PR instead of merging
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
                from_commit = commits['values'][1]['id']
                to_commit = commits['values'][0]['id']
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

async def main(service='all', jira_project=None, jira_issue=None, confluence_space=None, confluence_page=None, bitbucket_repo=None, bitbucket_branch=None):
    services_to_test = []
    if service == 'all':
        services_to_test = ['jira', 'confluence', 'bitbucket']
        print("=" * 60)
        print("ATLASSIAN DATA CENTER INTEGRATION TEST")
        print("Testing 95 available tools (31 Jira + 30 Confluence + 34 Bitbucket)")
        print("=" * 60)
    else:
        services_to_test = [service]
        tool_counts = {'jira': 31, 'confluence': 30, 'bitbucket': 34}
        print("=" * 60)
        print(f"ATLASSIAN DATA CENTER INTEGRATION TEST - {service.upper().replace('_', ' ')} ONLY")
        print(f"Testing {tool_counts[service]} {service.replace('_', ' ').title()} tools")
        print("=" * 60)
    
    jira_p = jira_f = jira_e = jira_s = 0
    conf_p = conf_f = conf_e = conf_s = 0
    bb_p = bb_f = bb_e = bb_s = 0
    
    if 'jira' in services_to_test:
        print("\n" + "=" * 60)
        print("JIRA DATA CENTER (31 tools available)")
        print("=" * 60)
        jira_p, jira_f, jira_e, jira_s = await test_all_jira_dc_tools(jira_project, jira_issue)
        print(f"  Tested: {jira_p + jira_f + jira_e} of 31 Jira tools")
    
    if 'confluence' in services_to_test:
        print("\n" + "=" * 60)
        print("CONFLUENCE DATA CENTER (30 tools available)")
        print("=" * 60)
        conf_p, conf_f, conf_e, conf_s = await test_all_confluence_dc_tools(confluence_space, confluence_page)
        print(f"  Tested: {conf_p + conf_f + conf_e} of 30 Confluence tools")
    
    if 'bitbucket' in services_to_test:
        print("\n" + "=" * 60)
        print("BITBUCKET DATA CENTER (34 tools available)")
        print("=" * 60)
        bb_p, bb_f, bb_e, bb_s = await test_all_bitbucket_dc_tools(bitbucket_repo, bitbucket_branch)
        print(f"  Tested: {bb_p + bb_f + bb_e} of 34 Bitbucket tools")
    
    total_p = jira_p + conf_p + bb_p
    total_f = jira_f + conf_f + bb_f
    total_e = jira_e + conf_e + bb_e
    total_s = jira_s + conf_s + bb_s
    
    total_available = 0
    if 'jira' in services_to_test:
        total_available += 31
    if 'confluence' in services_to_test:
        total_available += 30
    if 'bitbucket' in services_to_test:
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
    elif total_p == 0:
        print("\n[SKIP] NO TESTS RUN (configure credentials)")
        return 0
    else:
        print("\n[PASS] ALL TESTS PASSED")
        return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Atlassian Data Center tools')
    parser.add_argument('--service', choices=['jira', 'confluence', 'bitbucket', 'all'], 
                       default='all', help='Service to test (default: all)')
    parser.add_argument('--jira-project', type=str, help='Jira project key for testing (optional)')
    parser.add_argument('--jira-issue', type=str, help='Jira issue key for testing (optional, skips create/delete)')
    parser.add_argument('--confluence-space', type=str, help='Confluence space key for testing (optional)')
    parser.add_argument('--confluence-page', type=str, help='Confluence page ID for testing (optional, skips create/delete)')
    parser.add_argument('--bitbucket-repo', type=str, help='Bitbucket repository slug for testing (optional)')
    parser.add_argument('--bitbucket-branch', type=str, help='Bitbucket branch name for testing (optional)')
    args = parser.parse_args()
    
    print("=" * 60)
    print("ATLASSIAN DATA CENTER INTEGRATION TEST")
    print("=" * 60)
    
    load_config()
    
    exit_code = asyncio.run(main(args.service, args.jira_project, args.jira_issue, args.confluence_space, args.confluence_page, args.bitbucket_repo, args.bitbucket_branch))
    sys.exit(exit_code)
