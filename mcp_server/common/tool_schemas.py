"""JSON schemas for MCP tool inputs"""

TOOL_SCHEMAS = {
    # Jira tools
    "search_jira": {
        "type": "object",
        "properties": {
            "jql": {"type": "string", "description": "JQL query string"}
        },
        "required": ["jql"]
    },
    "get_issue": {
        "type": "object",
        "properties": {
            "issue_key": {"type": "string", "description": "Issue key (e.g., PROJ-123)"}
        },
        "required": ["issue_key"]
    },
    "create_issue": {
        "type": "object",
        "properties": {
            "project_key": {"type": "string"},
            "summary": {"type": "string"},
            "description": {"type": "string"},
            "issue_type": {"type": "string"},
            "custom_fields": {"type": "object", "description": "Optional custom fields as key-value pairs (e.g., {'customfield_10001': 'value'})"}
        },
        "required": ["project_key", "summary", "issue_type"]
    },
    "update_issue": {
        "type": "object",
        "properties": {
            "issue_key": {"type": "string"},
            "fields": {"type": "object"}
        },
        "required": ["issue_key", "fields"]
    },
    "add_comment": {
        "type": "object",
        "properties": {
            "issue_key": {"type": "string"},
            "comment": {"type": "string"}
        },
        "required": ["issue_key", "comment"]
    },
    "get_issue_comments": {
        "type": "object",
        "properties": {
            "issue_key": {"type": "string"}
        },
        "required": ["issue_key"]
    },
    "transition_issue": {
        "type": "object",
        "properties": {
            "issue_key": {"type": "string"},
            "transition_id": {"type": "string"}
        },
        "required": ["issue_key", "transition_id"]
    },
    "get_issue_transitions": {
        "type": "object",
        "properties": {
            "issue_key": {"type": "string"}
        },
        "required": ["issue_key"]
    },
    "assign_issue": {
        "type": "object",
        "properties": {
            "issue_key": {"type": "string"},
            "account_id": {"type": "string"}
        },
        "required": ["issue_key", "account_id"]
    },
    "delete_issue": {
        "type": "object",
        "properties": {
            "issue_key": {"type": "string"}
        },
        "required": ["issue_key"]
    },
    "list_projects": {
        "type": "object",
        "properties": {}
    },
    "get_project": {
        "type": "object",
        "properties": {
            "project_key": {"type": "string"}
        },
        "required": ["project_key"]
    },
    "get_issue_attachments": {
        "type": "object",
        "properties": {
            "issue_key": {"type": "string"}
        },
        "required": ["issue_key"]
    },
    "get_issue_watchers": {
        "type": "object",
        "properties": {
            "issue_key": {"type": "string"}
        },
        "required": ["issue_key"]
    },
    "search_by_assignee": {
        "type": "object",
        "properties": {
            "assignee": {"type": "string", "description": "Jira account ID or email address of the assignee. For current user, use 'currentUser()'."}
        },
        "required": ["assignee"]
    },
    "set_priority": {
        "type": "object",
        "properties": {
            "issue_key": {"type": "string", "description": "Issue key (e.g., PROJ-123)"},
            "priority": {"type": "string", "description": "Priority name (e.g., High, Medium, Low, Highest, Lowest)"}
        },
        "required": ["issue_key", "priority"]
    },
    
    # Confluence tools
    "search_confluence": {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    },
    "get_page": {
        "type": "object",
        "properties": {
            "page_id": {"type": "string"}
        },
        "required": ["page_id"]
    },
    "get_page_by_title": {
        "type": "object",
        "properties": {
            "space_key": {"type": "string"},
            "title": {"type": "string"}
        },
        "required": ["space_key", "title"]
    },
    "create_page": {
        "type": "object",
        "properties": {
            "space_key": {"type": "string"},
            "title": {"type": "string"},
            "content": {"type": "string"}
        },
        "required": ["space_key", "title", "content"]
    },
    "update_page": {
        "type": "object",
        "properties": {
            "page_id": {"type": "string"},
            "title": {"type": "string"},
            "content": {"type": "string"},
            "version": {"type": "integer"}
        },
        "required": ["page_id", "title", "content", "version"]
    },
    "delete_page": {
        "type": "object",
        "properties": {
            "page_id": {"type": "string"}
        },
        "required": ["page_id"]
    },
    "list_pages": {
        "type": "object",
        "properties": {
            "space_key": {"type": "string"}
        },
        "required": ["space_key"]
    },
    "get_space": {
        "type": "object",
        "properties": {
            "space_key": {"type": "string"}
        },
        "required": ["space_key"]
    },
    "list_spaces": {
        "type": "object",
        "properties": {}
    },
    "get_page_comments": {
        "type": "object",
        "properties": {
            "page_id": {"type": "string"}
        },
        "required": ["page_id"]
    },
    "add_page_comment": {
        "type": "object",
        "properties": {
            "page_id": {"type": "string"},
            "comment": {"type": "string"}
        },
        "required": ["page_id", "comment"]
    },
    "get_page_attachments": {
        "type": "object",
        "properties": {
            "page_id": {"type": "string"}
        },
        "required": ["page_id"]
    },
    "move_page": {
        "type": "object",
        "properties": {
            "page_id": {"type": "string"},
            "target_space_key": {"type": "string"},
            "target_parent_id": {"type": "string"}
        },
        "required": ["page_id", "target_space_key"]
    },
    "get_child_pages": {
        "type": "object",
        "properties": {
            "page_id": {"type": "string"}
        },
        "required": ["page_id"]
    },
    "get_descendants": {
        "type": "object",
        "properties": {
            "page_id": {"type": "string"}
        },
        "required": ["page_id"]
    },
    "get_ancestors": {
        "type": "object",
        "properties": {
            "page_id": {"type": "string"}
        },
        "required": ["page_id"]
    },
    "cql_search": {
        "type": "object",
        "properties": {
            "cql": {"type": "string", "description": "CQL query string. Examples: 'creator = currentUser()' to find pages you created, 'parent=123456', 'type=page AND space=DEV', 'label = mylabel'"},
            "limit": {"type": "integer"}
        },
        "required": ["cql"]
    },
    
    # Bitbucket tools
    "search_bitbucket": {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    },
    "get_repository": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"}
        },
        "required": ["repo_slug"]
    },
    "list_repositories": {
        "type": "object",
        "properties": {}
    },
    "list_pull_requests": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "state": {"type": "string", "enum": ["OPEN", "MERGED", "DECLINED"]}
        },
        "required": ["repo_slug"]
    },
    "get_pull_request": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "pr_id": {"type": "integer"}
        },
        "required": ["repo_slug", "pr_id"]
    },
    "create_pull_request": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "title": {"type": "string"},
            "source_branch": {"type": "string"},
            "dest_branch": {"type": "string"},
            "description": {"type": "string"}
        },
        "required": ["repo_slug", "title", "source_branch", "dest_branch"]
    },
    "get_file_content": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "file_path": {"type": "string"},
            "branch": {"type": "string"}
        },
        "required": ["repo_slug", "file_path"]
    },
    "list_commits": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "branch": {"type": "string"}
        },
        "required": ["repo_slug"]
    },
    "get_commit": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "commit_hash": {"type": "string"}
        },
        "required": ["repo_slug", "commit_hash"]
    },
    "list_branches": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string", "description": "Repository slug (e.g., atlassian_mcp)"}
        },
        "required": ["repo_slug"]
    },
    "get_pull_request_diff": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "pr_id": {"type": "integer"}
        },
        "required": ["repo_slug", "pr_id"]
    },
    "get_pull_request_comments": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "pr_id": {"type": "integer"}
        },
        "required": ["repo_slug", "pr_id"]
    },
    "add_pr_comment": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "pr_id": {"type": "integer"},
            "comment": {"type": "string"}
        },
        "required": ["repo_slug", "pr_id", "comment"]
    },
    "approve_pull_request": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "pr_id": {"type": "integer"}
        },
        "required": ["repo_slug", "pr_id"]
    },
    "merge_pull_request": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "pr_id": {"type": "integer"}
        },
        "required": ["repo_slug", "pr_id"]
    },
    "get_commit_diff": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "commit_hash": {"type": "string"}
        },
        "required": ["repo_slug", "commit_hash"]
    },
    "list_tags": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"}
        },
        "required": ["repo_slug"]
    },
    "list_directory": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "path": {"type": "string"},
            "branch": {"type": "string"}
        },
        "required": ["repo_slug"]
    },
    "update_pull_request": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "pr_id": {"type": "integer"},
            "title": {"type": "string"},
            "description": {"type": "string"}
        },
        "required": ["repo_slug", "pr_id"]
    },
    "compare_commits": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "from_commit": {"type": "string"},
            "to_commit": {"type": "string"}
        },
        "required": ["repo_slug", "from_commit", "to_commit"]
    },
    
    # Additional Jira schemas
    "get_user": {
        "type": "object",
        "properties": {
            "account_id": {"type": "string"}
        },
        "required": ["account_id"]
    },
    "search_users": {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    },
    "get_current_user": {
        "type": "object",
        "properties": {}
    },
    "link_issues": {
        "type": "object",
        "properties": {
            "inward_issue": {"type": "string"},
            "outward_issue": {"type": "string"},
            "link_type": {"type": "string"}
        },
        "required": ["inward_issue", "outward_issue"]
    },
    "add_worklog": {
        "type": "object",
        "properties": {
            "issue_key": {"type": "string"},
            "time_spent": {"type": "string", "description": "Time in Jira format (e.g., '2h 30m', '1d')"},
            "comment": {"type": "string"}
        },
        "required": ["issue_key", "time_spent"]
    },
    "get_worklogs": {
        "type": "object",
        "properties": {
            "issue_key": {"type": "string"}
        },
        "required": ["issue_key"]
    },
    "add_label": {
        "type": "object",
        "properties": {
            "issue_key": {"type": "string"},
            "label": {"type": "string"}
        },
        "required": ["issue_key", "label"]
    },
    "search_by_reporter": {
        "type": "object",
        "properties": {
            "reporter": {"type": "string"},
            "project_key": {"type": "string"}
        },
        "required": ["reporter"]
    },
    "get_recent_issues": {
        "type": "object",
        "properties": {
            "days": {"type": "integer"},
            "project_key": {"type": "string"}
        }
    },
    "list_boards": {
        "type": "object",
        "properties": {}
    },
    "get_board_issues": {
        "type": "object",
        "properties": {
            "board_id": {"type": "integer"}
        },
        "required": ["board_id"]
    },
    "list_sprints": {
        "type": "object",
        "properties": {
            "board_id": {"type": "integer"}
        },
        "required": ["board_id"]
    },
    "get_sprint_issues": {
        "type": "object",
        "properties": {
            "sprint_id": {"type": "integer"}
        },
        "required": ["sprint_id"]
    },
    "get_user_permissions": {
        "type": "object",
        "properties": {
            "project_key": {"type": "string"}
        }
    },
    "add_attachment": {
        "type": "object",
        "properties": {
            "issue_key": {"type": "string"},
            "filename": {"type": "string"},
            "content": {"type": "string", "description": "File content (will be converted to bytes)"}
        },
        "required": ["issue_key", "filename", "content"]
    },
    
    # Additional Confluence schemas
    "get_confluence_user": {
        "type": "object",
        "properties": {
            "account_id": {"type": "string"}
        },
        "required": ["account_id"]
    },
    "search_confluence_users": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Username or email to search. Note: May not work in some Data Center versions - use cql_search with 'creator = username' instead."}
        },
        "required": ["query"]
    },
    "add_page_label": {
        "type": "object",
        "properties": {
            "page_id": {"type": "string"},
            "label": {"type": "string"}
        },
        "required": ["page_id", "label"]
    },
    "get_page_labels": {
        "type": "object",
        "properties": {
            "page_id": {"type": "string"}
        },
        "required": ["page_id"]
    },
    "get_page_history": {
        "type": "object",
        "properties": {
            "page_id": {"type": "string"}
        },
        "required": ["page_id"]
    },
    "get_page_restrictions": {
        "type": "object",
        "properties": {
            "page_id": {"type": "string"}
        },
        "required": ["page_id"]
    },
    "set_page_restrictions": {
        "type": "object",
        "properties": {
            "page_id": {"type": "string"},
            "restrictions": {"type": "object"}
        },
        "required": ["page_id", "restrictions"]
    },
    "copy_page": {
        "type": "object",
        "properties": {
            "page_id": {"type": "string"},
            "new_title": {"type": "string"},
            "space_key": {"type": "string"}
        },
        "required": ["page_id", "new_title"]
    },
    "get_user_content": {
        "type": "object",
        "properties": {
            "account_id": {"type": "string"}
        },
        "required": ["account_id"]
    },
    "get_recent_content": {
        "type": "object",
        "properties": {
            "days": {"type": "integer", "description": "Number of days to look back (default: 7)"},
            "space_key": {"type": "string", "description": "Optional: Filter by space key"}
        }
    },
    "restore_page_version": {
        "type": "object",
        "properties": {
            "page_id": {"type": "string"},
            "version": {"type": "integer"}
        },
        "required": ["page_id", "version"]
    },
    "search_by_author": {
        "type": "object",
        "properties": {
            "account_id": {"type": "string"},
            "space_key": {"type": "string"}
        },
        "required": ["account_id"]
    },
    "search_by_label": {
        "type": "object",
        "properties": {
            "label": {"type": "string"}
        },
        "required": ["label"]
    },
    
    # Additional Bitbucket schemas
    "add_pr_reviewer": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "pr_id": {"type": "integer"},
            "account_id": {"type": "string"}
        },
        "required": ["repo_slug", "pr_id", "account_id"]
    },
    "decline_pull_request": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "pr_id": {"type": "integer"}
        },
        "required": ["repo_slug", "pr_id"]
    },
    "create_branch": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "branch_name": {"type": "string", "description": "New branch name"},
            "from_branch": {"type": "string", "description": "Source branch (default: main)"}
        },
        "required": ["repo_slug", "branch_name"]
    },
    "delete_branch": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "branch_name": {"type": "string"}
        },
        "required": ["repo_slug", "branch_name"]
    },
    "get_bitbucket_user": {
        "type": "object",
        "properties": {
            "username": {"type": "string"}
        },
        "required": ["username"]
    },
    "get_pr_activity": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "pr_id": {"type": "integer"}
        },
        "required": ["repo_slug", "pr_id"]
    },
    "get_default_reviewers": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"}
        },
        "required": ["repo_slug"]
    },
    "list_pull_requests_by_author": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "author": {"type": "string"}
        },
        "required": ["repo_slug", "author"]
    },
    "list_commits_by_author": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "author": {"type": "string"},
            "branch": {"type": "string"}
        },
        "required": ["repo_slug", "author"]
    },
    "request_changes": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "pr_id": {"type": "integer"},
            "comment": {"type": "string"}
        },
        "required": ["repo_slug", "pr_id"]
    },
    "get_branch_restrictions": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"}
        },
        "required": ["repo_slug"]
    },
    "get_build_status": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "commit_hash": {"type": "string"}
        },
        "required": ["repo_slug", "commit_hash"]
    },
    "create_webhook": {
        "type": "object",
        "properties": {
            "repo_slug": {"type": "string"},
            "url": {"type": "string"},
            "events": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["repo_slug", "url", "events"]
    }
}
