#!/usr/bin/env python3
"""Test Jira Cloud tools"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from mcp_server.cloud.jira_provider import JiraProvider

async def test_jira_tools():
    print("Testing Jira Cloud Tools...")
    jira = JiraProvider()
    
    print("\n1. Testing list_projects...")
    result = await jira.list_projects()
    projects = result.get('projects', [])
    print(f"Projects: {len(projects)} found")
    
    if not projects:
        print("No projects available")
        return
    
    # Show first 10 projects
    print("\nAvailable projects:")
    for i, proj in enumerate(projects[:10]):
        print(f"  {i+1}. {proj['key']} - {proj['name']}")
    
    project_key = input("\nEnter project key (or press Enter for default): ").strip()
    if not project_key:
        project_key = projects[0]['key']
        print(f"Using default: {project_key}")
    else:
        # Extract just the key if user entered full name
        project_key = project_key.split()[0] if ' ' in project_key else project_key
        print(f"Using project: {project_key}")
    
    # Get project details to find valid issue type
    proj_details = await jira.get_project(project_key)
    if 'error' in proj_details:
        print(f"Error getting project: {proj_details['error']}")
        return
    
    issue_types = proj_details.get('issueTypes', [])
    if not issue_types:
        print("No issue types available")
        return
    
    print("\nAvailable issue types:")
    for i, it in enumerate(issue_types):
        print(f"  {i+1}. {it['name']}")
    
    issue_type = input("\nEnter issue type to test with: ").strip()
    if not issue_type:
        issue_type = issue_types[0]['name']
        print(f"Using default: {issue_type}")
    else:
        print(f"Using issue type: {issue_type}")
    
    print("\n2. Testing create_issue...")
    
    # Try creating first to get error with required fields
    result = await jira.create_issue(project_key, "Test Issue", "Test Description", issue_type)
    
    if 'error' in result and 'errors' in result['error']:
        import json
        try:
            error_text = result['error'].split(' - ', 1)[1]
            error_json = json.loads(error_text)
            required_errors = error_json.get('errors', {})
            
            if required_errors:
                # Find existing issue to get example values
                search_result = await jira.search(f"project = {project_key} AND issuetype = '{issue_type}'")
                example_issue = None
                if search_result.get('results'):
                    example_key = search_result['results'][0]['key']
                    example_issue = await jira.get_issue(example_key)
                    print(f"  Using {example_key} as example")
                
                print(f"  Found {len(required_errors)} required fields:")
                custom_fields = {}
                description = "Test Description"
                
                for field_key in required_errors.keys():
                    field_url = f"{jira.auth.get_base_url()}/rest/api/2/field"
                    field_resp = jira.session.get(field_url, headers=jira.auth.get_auth_headers(), timeout=jira.timeout)
                    all_fields_meta = field_resp.json() if field_resp.status_code == 200 else []
                    
                    field_meta = next((f for f in all_fields_meta if f['id'] == field_key), None)
                    field_name = field_meta['name'] if field_meta else field_key
                    
                    if field_key == 'description':
                        description = 'Test Description'
                        print(f"    - {field_name}: Auto-filled")
                    else:
                        # Check if field is an object with ID (dropdown/select)
                        if example_issue and 'fields' in example_issue:
                            field_val = example_issue['fields'].get(field_key)
                            if field_val and isinstance(field_val, dict) and 'id' in field_val:
                                # Get all unique values from existing issues
                                search_url = f"{jira.auth.get_base_url()}/rest/api/2/search"
                                search_params = {'jql': f'project = {project_key} AND "{field_name}" is not EMPTY', 'maxResults': 100, 'fields': field_key}
                                search_resp = jira.session.get(search_url, headers=jira.auth.get_auth_headers(), params=search_params, timeout=jira.timeout)
                                
                                options = {}
                                if search_resp.status_code == 200:
                                    search_data = search_resp.json()
                                    for iss in search_data.get('issues', []):
                                        val = iss.get('fields', {}).get(field_key)
                                        if val and isinstance(val, dict) and 'id' in val:
                                            options[val['id']] = val['value']
                                
                                if options:
                                    print(f"    - {field_name}:")
                                    option_list = list(options.items())
                                    for i, (opt_id, opt_name) in enumerate(option_list[:20]):
                                        print(f"      {i+1}. {opt_name}")
                                    choice = input(f"      Enter number (1-{min(len(option_list), 20)}): ").strip()
                                    if choice.isdigit() and 1 <= int(choice) <= len(option_list):
                                        selected_id = option_list[int(choice)-1][0]
                                        custom_fields[field_key] = {"id": selected_id}
                                        continue
                        
                        # Text input with example for non-dropdown fields
                        example_val = ""
                        if example_issue and 'fields' in example_issue:
                            field_val = example_issue['fields'].get(field_key)
                            if field_val and not isinstance(field_val, dict):
                                example_val = f" (example: {field_val})"
                        
                        value = input(f"    - {field_name}{example_val}: ").strip()
                        if value:
                            custom_fields[field_key] = value
                
                # Retry with filled fields
                result = await jira.create_issue(project_key, "Test Issue", description, issue_type, custom_fields)
        except:
            pass
    
    created_issues = []
    if 'error' in result:
        print(f"Create: Failed - {result['error'][:150]}")
        print(f"Using existing issue for remaining tests...")
        search_result = await jira.search(f"project = {project_key}")
        if search_result.get('results'):
            issue_key = search_result['results'][0]['key']
            print(f"Issue: {issue_key}")
        else:
            return
    elif 'key' in result:
        issue_key = result['key']
        created_issues.append(issue_key)
        print(f"Create: {issue_key}")
    else:
        return
    
    print("\n3. Testing get_issue...")
    issue_result = await jira.get_issue(issue_key)
    if 'error' in issue_result:
        print(f"Get issue: {issue_result['error'][:50]}...")
    else:
        print(f"Get issue: {issue_key} retrieved")
    
    print("\n4. Testing search_jira...")
    search_result = await jira.search(f"project = {project_key}")
    print(f"Search: {search_result.get('total', 0)} issues found")
    
    if created_issues:
        print("\nCleaning up created issues:")
        for issue in created_issues:
            result = await jira.delete_issue(issue)
            if 'error' in result:
                # Try closing instead
                transitions = await jira.get_issue_transitions(issue)
                close_transition = None
                for trans in transitions.get('transitions', []):
                    if 'close' in trans['name'].lower() or 'done' in trans['name'].lower():
                        close_transition = trans['id']
                        break
                if close_transition:
                    await jira.transition_issue(issue, close_transition)
                    print(f"  Closed: {issue} (delete permission denied)")
                else:
                    print(f"  Could not clean up {issue}")
            else:
                print(f"  Deleted: {issue}")
    
    print("\nJira Cloud tools test completed!")

if __name__ == "__main__":
    asyncio.run(test_jira_tools())
