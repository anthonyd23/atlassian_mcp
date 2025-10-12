#!/usr/bin/env python3
"""Test all 14 Jira tools"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from mcp_server.cloud.jira_provider import JiraProvider

async def test_jira_tools():
    print("Testing Jira Tools...\n")
    jira = JiraProvider()
    
    # 1. List projects
    print("1. list_projects")
    result = await jira.list_projects()
    print(f"   Result: {result}\n")
    
    # 2. Get project
    print("2. get_project")
    result = await jira.get_project("AM")
    print(f"   Result: {result}\n")
    
    # 3. Search issues
    print("3. search_jira")
    result = await jira.search("project = AM")
    print(f"   Result: {result}\n")
    
    # 4. Create issue
    print("4. create_issue")
    result = await jira.create_issue("AM", "Test Issue", "Testing MCP tools", "Task")
    issue_key = result.get('key') if 'key' in result else None
    print(f"   Result: {result}\n")
    
    if issue_key:
        # 5. Get issue
        print("5. get_issue")
        result = await jira.get_issue(issue_key)
        print(f"   Result: {result}\n")
        
        # 6. Update issue
        print("6. update_issue")
        result = await jira.update_issue(issue_key, {"summary": "Updated Test Issue"})
        print(f"   Result: {result}\n")
        
        # 7. Add comment
        print("7. add_comment")
        result = await jira.add_comment(issue_key, "Test comment from MCP")
        print(f"   Result: {result}\n")
        
        # 8. Get issue comments
        print("8. get_issue_comments")
        result = await jira.get_issue_comments(issue_key)
        print(f"   Result: {result}\n")
        
        # 9. Get issue transitions
        print("9. get_issue_transitions")
        result = await jira.get_issue_transitions(issue_key)
        print(f"   Result: {result}\n")
        
        # 10. Get issue attachments
        print("10. get_issue_attachments")
        result = await jira.get_issue_attachments(issue_key)
        print(f"   Result: {result}\n")
        
        # 11. Get issue watchers
        print("11. get_issue_watchers")
        result = await jira.get_issue_watchers(issue_key)
        print(f"   Result: {result}\n")
        
        # 12. Assign issue (skip - needs account_id)
        print("12. assign_issue - SKIPPED (needs account_id)\n")
        
        # 13. Transition issue (skip - needs transition_id)
        print("13. transition_issue - SKIPPED (needs transition_id)\n")
        
        # 14. Delete issue
        print("14. delete_issue")
        result = await jira.delete_issue(issue_key)
        print(f"   Result: {result}\n")
    
    print("Jira tools test completed!")

if __name__ == "__main__":
    asyncio.run(test_jira_tools())
