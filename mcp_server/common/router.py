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
        return await jira.create_issue(arguments["project_key"], arguments["summary"], arguments["description"], arguments.get("issue_type", "Task"), arguments.get("custom_fields"))
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
    elif name == "get_user":
        return await jira.get_user(arguments["account_id"])
    elif name == "search_users":
        return await jira.search_users(arguments["query"])
    elif name == "get_current_user":
        return await jira.get_current_user()
    elif name == "link_issues":
        return await jira.link_issues(arguments["inward_issue"], arguments["outward_issue"], arguments.get("link_type", "Relates"))
    elif name == "add_worklog":
        return await jira.add_worklog(arguments["issue_key"], arguments["time_spent"], arguments.get("comment", ""))
    elif name == "get_worklogs":
        return await jira.get_worklogs(arguments["issue_key"])
    elif name == "add_label":
        return await jira.add_label(arguments["issue_key"], arguments["label"])
    elif name == "search_by_assignee":
        return await jira.search_by_assignee(arguments["assignee"], arguments.get("project_key", ""))
    elif name == "search_by_reporter":
        return await jira.search_by_reporter(arguments["reporter"], arguments.get("project_key", ""))
    elif name == "get_recent_issues":
        return await jira.get_recent_issues(arguments.get("days", 7), arguments.get("project_key", ""))
    elif name == "set_priority":
        return await jira.set_priority(arguments["issue_key"], arguments["priority"])
    elif name == "list_boards":
        return await jira.list_boards()
    elif name == "get_board_issues":
        return await jira.get_board_issues(arguments["board_id"])
    elif name == "list_sprints":
        return await jira.list_sprints(arguments["board_id"])
    elif name == "get_sprint_issues":
        return await jira.get_sprint_issues(arguments["sprint_id"])
    elif name == "get_user_permissions":
        return await jira.get_user_permissions(arguments.get("project_key", ""))
    elif name == "add_attachment":
        return await jira.add_attachment(arguments["issue_key"], arguments["filename"], arguments["content"])
    
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
    elif name == "get_confluence_user":
        return await confluence.get_user(arguments["account_id"])
    elif name == "search_confluence_users":
        return await confluence.search_users(arguments["query"])
    elif name == "add_page_label":
        return await confluence.add_label(arguments["page_id"], arguments["label"])
    elif name == "get_page_labels":
        return await confluence.get_labels(arguments["page_id"])
    elif name == "get_page_history":
        return await confluence.get_page_history(arguments["page_id"])
    elif name == "get_page_restrictions":
        return await confluence.get_page_restrictions(arguments["page_id"])
    elif name == "set_page_restrictions":
        return await confluence.set_page_restrictions(arguments["page_id"], arguments["restrictions"])
    elif name == "copy_page":
        return await confluence.copy_page(arguments["page_id"], arguments["new_title"], arguments.get("space_key", ""))
    elif name == "get_user_content":
        return await confluence.get_user_content(arguments["account_id"])
    elif name == "get_recent_content":
        return await confluence.get_recent_content(arguments.get("days", 7), arguments.get("space_key", ""))
    elif name == "restore_page_version":
        return await confluence.restore_page_version(arguments["page_id"], arguments["version"])
    elif name == "search_by_author":
        return await confluence.search_by_author(arguments["account_id"], arguments.get("space_key", ""))
    elif name == "search_by_label":
        return await confluence.search_by_label(arguments["label"], arguments.get("space_key", ""))
    elif name == "move_page":
        return await confluence.move_page(arguments["page_id"], arguments["target_space_key"], arguments.get("target_parent_id"))
    elif name == "get_child_pages":
        return await confluence.get_child_pages(arguments["page_id"])
    elif name == "get_descendants":
        return await confluence.get_descendants(arguments["page_id"])
    elif name == "get_ancestors":
        return await confluence.get_ancestors(arguments["page_id"])
    elif name == "cql_search":
        return await confluence.cql_search(arguments["cql"], arguments.get("limit", 25))
    
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
    elif name == "add_pr_reviewer":
        return await bitbucket.add_pr_reviewer(arguments["repo_slug"], arguments["pr_id"], arguments["account_id"])
    elif name == "decline_pull_request":
        return await bitbucket.decline_pull_request(arguments["repo_slug"], arguments["pr_id"])
    elif name == "create_branch":
        return await bitbucket.create_branch(arguments["repo_slug"], arguments["branch_name"], arguments.get("from_branch", "main"))
    elif name == "delete_branch":
        return await bitbucket.delete_branch(arguments["repo_slug"], arguments["branch_name"])
    elif name == "get_bitbucket_user":
        return await bitbucket.get_user(arguments["username"])
    elif name == "get_pr_activity":
        return await bitbucket.get_pr_activity(arguments["repo_slug"], arguments["pr_id"])
    elif name == "get_default_reviewers":
        return await bitbucket.get_default_reviewers(arguments["repo_slug"])
    elif name == "list_pull_requests_by_author":
        return await bitbucket.list_pull_requests_by_author(arguments["repo_slug"], arguments["author"])
    elif name == "list_commits_by_author":
        return await bitbucket.list_commits_by_author(arguments["repo_slug"], arguments["author"], arguments.get("branch", "main"))
    elif name == "request_changes":
        return await bitbucket.request_changes(arguments["repo_slug"], arguments["pr_id"], arguments.get("comment", ""))
    elif name == "get_branch_restrictions":
        return await bitbucket.get_branch_restrictions(arguments["repo_slug"])
    elif name == "get_build_status":
        return await bitbucket.get_build_status(arguments["repo_slug"], arguments["commit_hash"])
    elif name == "create_webhook":
        return await bitbucket.create_webhook(arguments["repo_slug"], arguments["url"], arguments.get("events", []))
    
    else:
        raise ValueError(f"Unknown tool: {name}")
