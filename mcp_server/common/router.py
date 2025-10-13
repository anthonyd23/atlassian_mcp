"""Shared tool routing logic for MCP server and Lambda handler"""
from typing import Dict, Any

async def route_tool_call(name: str, arguments: Dict[str, Any], jira, confluence, bitbucket) -> Dict[str, Any]:
    """Route tool calls to appropriate provider methods"""
    
    # Jira tools
    if name == "search_jira":
        return await jira.search(arguments["jql"])
    elif name == "get_issue":
        return await jira.get_issue(arguments["issue_key"])
    elif name == "create_issue":
        return await jira.create_issue(arguments["project_key"], arguments["summary"], arguments["description"], arguments.get("issue_type", "Task"))
    elif name == "update_issue":
        return await jira.update_issue(arguments["issue_key"], arguments["fields"])
    elif name == "add_comment":
        return await jira.add_comment(arguments["issue_key"], arguments["comment"])
    elif name == "get_issue_comments":
        return await jira.get_issue_comments(arguments["issue_key"])
    elif name == "transition_issue":
        return await jira.transition_issue(arguments["issue_key"], arguments["transition_id"])
    elif name == "get_issue_transitions":
        return await jira.get_issue_transitions(arguments["issue_key"])
    elif name == "assign_issue":
        return await jira.assign_issue(arguments["issue_key"], arguments["account_id"])
    elif name == "delete_issue":
        return await jira.delete_issue(arguments["issue_key"])
    elif name == "list_projects":
        return await jira.list_projects()
    elif name == "get_project":
        return await jira.get_project(arguments["project_key"])
    elif name == "get_issue_attachments":
        return await jira.get_issue_attachments(arguments["issue_key"])
    elif name == "get_issue_watchers":
        return await jira.get_issue_watchers(arguments["issue_key"])
    
    # Confluence tools
    elif name == "search_confluence":
        return await confluence.search(arguments["query"])
    elif name == "get_page":
        return await confluence.get_page(arguments["page_id"])
    elif name == "get_page_by_title":
        return await confluence.get_page_by_title(arguments["space_key"], arguments["title"])
    elif name == "create_page":
        return await confluence.create_page(arguments["space_key"], arguments["title"], arguments["content"], arguments.get("parent_id"))
    elif name == "update_page":
        return await confluence.update_page(arguments["page_id"], arguments["title"], arguments["content"], arguments["version"])
    elif name == "delete_page":
        return await confluence.delete_page(arguments["page_id"])
    elif name == "list_pages":
        return await confluence.list_pages(arguments["space_key"])
    elif name == "get_space":
        return await confluence.get_space(arguments["space_key"])
    elif name == "list_spaces":
        return await confluence.list_spaces()
    elif name == "get_page_comments":
        return await confluence.get_page_comments(arguments["page_id"])
    elif name == "add_page_comment":
        return await confluence.add_page_comment(arguments["page_id"], arguments["comment"])
    elif name == "get_page_attachments":
        return await confluence.get_page_attachments(arguments["page_id"])
    
    # Bitbucket tools
    elif name == "search_bitbucket":
        return await bitbucket.search(arguments["query"])
    elif name == "get_repository":
        return await bitbucket.get_repository(arguments["repo_slug"])
    elif name == "list_repositories":
        return await bitbucket.list_repositories()
    elif name == "list_pull_requests":
        return await bitbucket.list_pull_requests(arguments["repo_slug"], arguments.get("state", "OPEN"))
    elif name == "get_pull_request":
        return await bitbucket.get_pull_request(arguments["repo_slug"], arguments["pr_id"])
    elif name == "create_pull_request":
        return await bitbucket.create_pull_request(arguments["repo_slug"], arguments["title"], arguments["source_branch"], arguments["dest_branch"], arguments.get("description", ""))
    elif name == "get_file_content":
        return await bitbucket.get_file_content(arguments["repo_slug"], arguments["file_path"], arguments.get("branch", "main"))
    elif name == "list_commits":
        return await bitbucket.list_commits(arguments["repo_slug"], arguments.get("branch", "main"))
    elif name == "get_commit":
        return await bitbucket.get_commit(arguments["repo_slug"], arguments["commit_hash"])
    elif name == "list_branches":
        return await bitbucket.list_branches(arguments["repo_slug"])
    elif name == "get_pull_request_diff":
        return await bitbucket.get_pull_request_diff(arguments["repo_slug"], arguments["pr_id"])
    elif name == "get_pull_request_comments":
        return await bitbucket.get_pull_request_comments(arguments["repo_slug"], arguments["pr_id"])
    elif name == "add_pr_comment":
        return await bitbucket.add_pr_comment(arguments["repo_slug"], arguments["pr_id"], arguments["comment"])
    elif name == "approve_pull_request":
        return await bitbucket.approve_pull_request(arguments["repo_slug"], arguments["pr_id"])
    elif name == "merge_pull_request":
        return await bitbucket.merge_pull_request(arguments["repo_slug"], arguments["pr_id"])
    elif name == "get_commit_diff":
        return await bitbucket.get_commit_diff(arguments["repo_slug"], arguments["commit_hash"])
    elif name == "list_tags":
        return await bitbucket.list_tags(arguments["repo_slug"])
    elif name == "list_directory":
        return await bitbucket.list_directory(arguments["repo_slug"], arguments.get("path", ""), arguments.get("branch", "main"))
    elif name == "update_pull_request":
        return await bitbucket.update_pull_request(arguments["repo_slug"], arguments["pr_id"], arguments.get("title"), arguments.get("description"))
    elif name == "compare_commits":
        return await bitbucket.compare_commits(arguments["repo_slug"], arguments["from_commit"], arguments["to_commit"])
    
    else:
        raise ValueError(f"Unknown tool: {name}")
