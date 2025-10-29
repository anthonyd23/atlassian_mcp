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
            "title": {"type": "string"},
            "space_key": {"type": "string"}
        },
        "required": ["title", "space_key"]
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
            "cql": {"type": "string", "description": "CQL query string (e.g., 'parent=123456' or 'type=page AND space=DEV')"},
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
    }
}
