# Atlassian MCP Server

A comprehensive Model Context Protocol (MCP) server for Atlassian tools (Jira, Confluence, and Bitbucket) with 50 tools deployed on AWS Lambda.

## Features

- **50 MCP Tools**: Complete integration with Jira (14 tools), Confluence (12 tools), and Bitbucket (24 tools)
- **Jira Integration**: Search, create, update, delete issues, manage comments, transitions, and more
- **Confluence Integration**: Search, create, update pages, manage spaces, comments, and attachments
- **Bitbucket Integration**: Repository management, pull requests, commits, branches, file operations
- **AWS Deployment**: Serverless deployment using Lambda and API Gateway
- **Comprehensive Testing**: Full test suite for all 50 tools

## Prerequisites

1. **Atlassian API Token**: Generate from https://id.atlassian.com/manage-profile/security/api-tokens
2. **Bitbucket API Token**: Generate from https://bitbucket.org/account/settings/app-passwords/ (if using Bitbucket)
3. **AWS CLI**: Configured with appropriate permissions
4. **SAM CLI**: For deployment to AWS

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r mcp_server/requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   # Required for Jira and Confluence
   export ATLASSIAN_BASE_URL="https://yourcompany.atlassian.net"
   export ATLASSIAN_USERNAME="your-email@company.com"
   export ATLASSIAN_API_TOKEN="your-api-token"
   
   # Required for Bitbucket Cloud
   export BITBUCKET_WORKSPACE="your-workspace-name"  # Found in your Bitbucket URL
   export BITBUCKET_API_TOKEN="your-bitbucket-token"  # From https://bitbucket.org/account/settings/app-passwords/
   ```

3. **Test locally**:
   ```bash
   # Test all 50 tools
   python test_all_tools.py
   
   # Or test individual services
   python test_jira_tools.py
   python test_confluence_tools.py
   python test_bitbucket_tools.py
   ```

4. **Deploy to AWS**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

## MCP Tools (50 Total)

### Jira Tools (14)

**Search & Read:**
1. `search_jira` - Search issues using JQL queries (e.g., "project = PROJ AND status = Open")
2. `get_issue` - Get full details of a specific issue by key (e.g., PROJ-123)
3. `list_projects` - List all accessible Jira projects
4. `get_project` - Get detailed information about a specific project
5. `get_issue_comments` - Retrieve all comments on an issue
6. `get_issue_transitions` - Get available status transitions for an issue
7. `get_issue_attachments` - List all attachments on an issue
8. `get_issue_watchers` - Get list of users watching an issue

**Create & Update:**
9. `create_issue` - Create a new Jira issue with summary, description, and type
10. `update_issue` - Update any fields on an existing issue
11. `add_comment` - Add a comment to an issue
12. `transition_issue` - Move issue to a different status (e.g., In Progress, Done)
13. `assign_issue` - Assign an issue to a specific user
14. `delete_issue` - Permanently delete an issue

### Confluence Tools (12)

**Search & Read:**
1. `search_confluence` - Full-text search across all pages and spaces
2. `get_page` - Get page content and metadata by page ID
3. `get_page_by_title` - Find and retrieve a page by its title and space
4. `list_pages` - List all pages in a specific space
5. `get_space` - Get detailed information about a space
6. `list_spaces` - List all accessible Confluence spaces
7. `get_page_comments` - Retrieve all comments on a page
8. `get_page_attachments` - List all files attached to a page

**Create & Update:**
9. `create_page` - Create a new page with HTML/storage format content
10. `update_page` - Update page title and content (requires version number)
11. `add_page_comment` - Add a comment to a page
12. `delete_page` - Permanently delete a page

### Bitbucket Tools (24)

**Repository Operations:**
1. `search_bitbucket` - Search repositories by name or description
2. `get_repository` - Get detailed repository information
3. `list_repositories` - List all repositories in workspace
4. `list_branches` - List all branches in a repository
5. `list_tags` - List all tags in a repository
6. `list_directory` - List files and folders in a directory path
7. `get_file_content` - Get raw content of a specific file

**Commit Operations:**
8. `list_commits` - List commits in a branch with pagination
9. `get_commit` - Get detailed information about a specific commit
10. `get_commit_diff` - Get the diff/changes for a commit
11. `compare_commits` - Compare differences between two commits

**Pull Request Operations:**
12. `list_pull_requests` - List pull requests (filter by OPEN, MERGED, DECLINED)
13. `get_pull_request` - Get detailed PR information
14. `create_pull_request` - Create a new pull request from source to destination branch
15. `update_pull_request` - Update PR title or description
16. `get_pull_request_diff` - Get the full diff for a pull request
17. `get_pull_request_comments` - Retrieve all comments on a PR
18. `add_pr_comment` - Add a comment to a pull request
19. `approve_pull_request` - Approve a pull request
20. `merge_pull_request` - Merge an approved pull request

**Note:** Tools 21-24 are covered in the operations above (some tools were consolidated)

## MCP Resources

- `atlassian://bitbucket/repositories` - Access Bitbucket repositories
- `atlassian://confluence/spaces` - Access Confluence spaces  
- `atlassian://jira/projects` - Access Jira projects

## Configuration

### Environment Variables

**Required:**
- `ATLASSIAN_BASE_URL` - Your Atlassian instance URL (e.g., https://yourcompany.atlassian.net)
- `ATLASSIAN_USERNAME` - Your Atlassian email address
- `ATLASSIAN_API_TOKEN` - Your Atlassian API token (for Jira & Confluence)

**Optional (for Bitbucket Cloud):**
- `BITBUCKET_WORKSPACE` - Your Bitbucket workspace name (found in URL: bitbucket.org/WORKSPACE_NAME)
- `BITBUCKET_API_TOKEN` - Bitbucket API token (create at https://bitbucket.org/account/settings/app-passwords/ with Repositories:Read/Write permissions)

## Testing

Run comprehensive tests for all 50 tools:

```bash
# Test all tools
python test_all_tools.py

# Test individual services
python test_jira_tools.py        # 14 Jira tools
python test_confluence_tools.py  # 12 Confluence tools
python test_bitbucket_tools.py   # 24 Bitbucket tools
```

## AWS Deployment

The server deploys as a Lambda function with API Gateway:

```bash
./deploy.sh
```

Once deployed, you'll receive an API Gateway URL:
- `POST /mcp` - Main MCP protocol endpoint
- `GET /mcp` - Health check

## Security

- API tokens stored as encrypted environment variables in Lambda
- All API calls use HTTPS
- Basic authentication with Atlassian APIs
- No credentials stored in code

## Project Structure

```
atlassian_mcp/
├── mcp_server/
│   ├── main.py                 # MCP server implementation
│   ├── tools.py                # All 50 tool definitions
│   ├── auth.py                 # Authentication handler
│   ├── jira_provider.py        # Jira API integration
│   ├── confluence_provider.py  # Confluence API integration
│   ├── bitbucket_provider.py   # Bitbucket API integration
│   └── requirements.txt        # Python dependencies
├── lambda_handler.py           # AWS Lambda handler
├── template.yaml               # SAM deployment template
├── deploy.sh                   # Deployment script
├── test_all_tools.py          # Master test suite
├── test_jira_tools.py         # Jira tools tests
├── test_confluence_tools.py   # Confluence tools tests
├── test_bitbucket_tools.py    # Bitbucket tools tests
└── README.md                   # This file
```

## API Documentation

- [Jira REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v2/)
- [Confluence REST API](https://developer.atlassian.com/cloud/confluence/rest/v2/)
- [Bitbucket Cloud REST API](https://developer.atlassian.com/cloud/bitbucket/rest/)

## License

MIT
