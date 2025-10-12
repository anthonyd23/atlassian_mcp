# Atlassian MCP Server

A Model Context Protocol (MCP) server for Atlassian tools (Jira, Confluence, and Bitbucket) with 46 tools deployed on AWS Lambda.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [MCP Tools (46 Total)](#mcp-tools-46-total)
  - [Jira Tools (14)](#jira-tools-14)
  - [Confluence Tools (12)](#confluence-tools-12)
  - [Bitbucket Tools (20)](#bitbucket-tools-20)
- [MCP Resources](#mcp-resources)
- [Configuration](#configuration)
- [Testing](#testing)
- [AWS Deployment](#aws-deployment)
- [Amazon Q Integration](#amazon-q-integration)
- [Security](#security)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [License](#license)

## Features

- **46 MCP Tools**: Complete integration with Jira (14 tools), Confluence (12 tools), and Bitbucket (20 tools)
- **Dual Platform Support**: Works with both Atlassian Cloud and Data Center/Server deployments
- **Jira Integration**: Search, create, update, delete issues, manage comments, transitions, and more
- **Confluence Integration**: Search, create, update pages, manage spaces, comments, and attachments
- **Bitbucket Integration**: Repository management, pull requests, commits, branches, file operations
- **AWS Deployment**: Serverless deployment using Lambda and API Gateway
- **Comprehensive Testing**: Full test suite for all 46 tools on both platforms

## Prerequisites

### For Atlassian Cloud:
1. **Atlassian API Token**: Generate from https://id.atlassian.com/manage-profile/security/api-tokens
2. **Bitbucket API Token**: Generate from https://bitbucket.org/account/settings/app-passwords/ (if using Bitbucket Cloud)

### For Atlassian Data Center/Server:
1. **Personal Access Token (PAT)**: Generate from your Atlassian instance (Profile → Personal Access Tokens)
2. **Bitbucket Server Access**: Personal Access Token from Bitbucket Server

### For AWS Deployment:
3. **AWS CLI**: Configured with appropriate permissions
4. **SAM CLI**: For deployment to AWS

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r mcp_server/requirements.txt
   ```

2. **Set environment variables**:
   
   **For Atlassian Cloud:**
   ```bash
   # Required for Jira and Confluence Cloud
   export ATLASSIAN_BASE_URL="https://yourcompany.atlassian.net"
   export ATLASSIAN_USERNAME="your-email@company.com"
   export ATLASSIAN_API_TOKEN="your-api-token"
   
   # Required for Bitbucket Cloud
   export BITBUCKET_WORKSPACE="your-workspace-name"  # Found in your Bitbucket URL
   export BITBUCKET_API_TOKEN="your-bitbucket-token"  # From https://bitbucket.org/account/settings/app-passwords/
   ```
   
   **For Atlassian Data Center/Server:**
   ```bash
   # Required for Jira and Confluence Data Center
   export ATLASSIAN_BASE_URL="https://jira.yourcompany.com"
   export ATLASSIAN_PAT_TOKEN="your-personal-access-token"
   
   # Required for Bitbucket Server
   export BITBUCKET_PROJECT="YOUR_PROJECT_KEY"  # Your Bitbucket project key
   ```

3. **Test locally**:
   
   **For Cloud:**
   ```bash
   # Test all 46 Cloud tools
   python tests/cloud/test_all_tools.py
   
   # Or test individual services
   python tests/cloud/test_jira_tools.py
   python tests/cloud/test_confluence_tools.py
   python tests/cloud/test_bitbucket_tools.py
   ```
   
   **For Data Center:**
   ```bash
   # Test all 46 Data Center tools
   python tests/datacenter/test_all_dc_tools.py
   
   # Or test individual services
   python tests/datacenter/test_jira_dc_tools.py
   python tests/datacenter/test_confluence_dc_tools.py
   python tests/datacenter/test_bitbucket_dc_tools.py
   ```

4. **Deploy to AWS**:
   ```bash
   sam build
   sam deploy --guided
   ```

## MCP Tools (46 Total)

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

### Bitbucket Tools (20)

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

## MCP Resources

- `atlassian://bitbucket/repositories` - Access Bitbucket repositories
- `atlassian://confluence/spaces` - Access Confluence spaces  
- `atlassian://jira/projects` - Access Jira projects

## Configuration

### Environment Variables

**For Atlassian Cloud:**
- `ATLASSIAN_BASE_URL` - Your Atlassian Cloud URL (e.g., https://yourcompany.atlassian.net)
- `ATLASSIAN_USERNAME` - Your Atlassian email address
- `ATLASSIAN_API_TOKEN` - Your Atlassian API token (for Jira & Confluence Cloud)
- `BITBUCKET_WORKSPACE` - Your Bitbucket workspace name (found in URL: bitbucket.org/WORKSPACE_NAME)
- `BITBUCKET_API_TOKEN` - Bitbucket Cloud API token (create at https://bitbucket.org/account/settings/app-passwords/)

**For Atlassian Data Center/Server:**
- `ATLASSIAN_BASE_URL` - Your Data Center instance URL (e.g., https://jira.yourcompany.com)
- `ATLASSIAN_PAT_TOKEN` - Personal Access Token from your Data Center instance
- `BITBUCKET_PROJECT` - Your Bitbucket Server project key

**Platform Detection:**
The server automatically detects the platform:
- If `ATLASSIAN_PAT_TOKEN` is set → Data Center mode
- Otherwise → Cloud mode

## Testing

Run comprehensive tests for all 46 tools:

**Cloud Testing:**
```bash
# Test all Cloud tools
python tests/cloud/test_all_tools.py

# Test individual Cloud services
python tests/cloud/test_jira_tools.py        # 14 Jira tools
python tests/cloud/test_confluence_tools.py  # 12 Confluence tools
python tests/cloud/test_bitbucket_tools.py   # 20 Bitbucket tools
```

**Data Center Testing:**
```bash
# Test all Data Center tools
python tests/datacenter/test_all_dc_tools.py

# Test individual Data Center services
python tests/datacenter/test_jira_dc_tools.py        # 14 Jira tools
python tests/datacenter/test_confluence_dc_tools.py  # 12 Confluence tools
python tests/datacenter/test_bitbucket_dc_tools.py   # 20 Bitbucket Server tools
```

## AWS Deployment

The server deploys as a Lambda function with API Gateway:

```bash
sam build
sam deploy --guided
```

Once deployed, you'll receive:
- **API Gateway URL**: `https://<api-id>.execute-api.<region>.amazonaws.com/Prod/mcp`
- **API Key ID**: Use to retrieve your API key

### Retrieve Your API Key

After deployment, get your API key:

```bash
# Get the API Key ID from deployment output
aws apigateway get-api-key --api-key <API_KEY_ID> --include-value --query "value" --output text
```

### API Endpoints

- `POST /mcp` - Main MCP protocol endpoint
- `GET /mcp` - Health check

**All requests require the `x-api-key` header:**

```bash
curl -H "x-api-key: YOUR_API_KEY" \
  https://<api-id>.execute-api.<region>.amazonaws.com/Prod/mcp
```

### Rate Limits

- **Rate**: 100 requests/second
- **Burst**: 200 requests

## Amazon Q Integration

Connect this MCP server to Amazon Q Developer for AI-powered Atlassian workflows.

### Setup in Amazon Q Developer

1. Open Amazon Q Developer settings
2. Navigate to **Settings → MCP Servers → Add Server**
3. Configure the server:

**For Atlassian Cloud:**
```json
{
  "mcpServers": {
    "atlassian-mcp": {
      "command": "python",
      "args": ["/absolute/path/to/atlassian_mcp/mcp_server/main.py"],
      "env": {
        "ATLASSIAN_BASE_URL": "https://yourcompany.atlassian.net",
        "ATLASSIAN_USERNAME": "your-email@company.com",
        "ATLASSIAN_API_TOKEN": "your-api-token",
        "BITBUCKET_WORKSPACE": "your-workspace",
        "BITBUCKET_API_TOKEN": "your-bitbucket-token"
      }
    }
  }
}
```

**For Atlassian Data Center:**
```json
{
  "mcpServers": {
    "atlassian-mcp": {
      "command": "python",
      "args": ["/absolute/path/to/atlassian_mcp/mcp_server/main.py"],
      "env": {
        "ATLASSIAN_BASE_URL": "https://jira.yourcompany.com",
        "ATLASSIAN_PAT_TOKEN": "your-personal-access-token",
        "BITBUCKET_PROJECT": "YOUR_PROJECT_KEY"
      }
    }
  }
}
```

### Testing the Connection

Once configured, test the connection in Amazon Q:

```
# List available tools
"What Atlassian tools are available?"

# Search Jira
"Search for open issues in project PROJ"

# Get issue details
"Show me details for PROJ-123"

# Search Confluence
"Find Confluence pages about deployment"

# List repositories
"What Bitbucket repositories do we have?"
```

### Example Workflows

**Create a Jira issue:**
```
"Create a Jira issue in project PROJ with summary 'Fix login bug' and description 'Users cannot log in'"
```

**Update Confluence page:**
```
"Update Confluence page 12345 with new deployment instructions"
```

**Review pull request:**
```
"Show me the diff for pull request 42 in repo my-app"
```

## Security

### API Gateway Authentication

- **API Key Required**: All Lambda endpoints require `x-api-key` header
- **Rate Limiting**: 100 req/sec with 200 burst capacity
- **HTTPS Only**: All traffic encrypted in transit

### Credential Management

- API tokens stored as encrypted environment variables in Lambda
- Cloud: Basic authentication with API tokens
- Data Center: Bearer token authentication with Personal Access Tokens
- No credentials stored in code

### For Public Deployment

If sharing this project:
1. Users deploy their own Lambda stack
2. Each user gets their own API key
3. Set `AWS_LAMBDA_API_KEY` environment variable when using Lambda mode

## Project Structure

```
atlassian_mcp/
├── mcp_server/
│   ├── common/
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication (Cloud & Data Center)
│   │   └── tools.py            # All 46 tool definitions
│   ├── cloud/
│   │   ├── __init__.py
│   │   ├── jira_provider.py        # Jira Cloud API integration
│   │   ├── confluence_provider.py  # Confluence Cloud API integration
│   │   └── bitbucket_provider.py   # Bitbucket Cloud API integration
│   ├── datacenter/
│   │   ├── __init__.py
│   │   ├── jira_dc_provider.py        # Jira Data Center API integration
│   │   ├── confluence_dc_provider.py  # Confluence Data Center API integration
│   │   └── bitbucket_dc_provider.py   # Bitbucket Server API integration
│   ├── __init__.py
│   ├── main.py                 # MCP server implementation
│   └── requirements.txt        # MCP server dependencies
├── tests/
│   ├── cloud/
│   │   ├── __init__.py
│   │   ├── test_all_tools.py       # Cloud master test suite
│   │   ├── test_jira_tools.py      # Jira Cloud tests
│   │   ├── test_confluence_tools.py # Confluence Cloud tests
│   │   └── test_bitbucket_tools.py # Bitbucket Cloud tests
│   ├── datacenter/
│   │   ├── __init__.py
│   │   ├── test_all_dc_tools.py       # Data Center master test suite
│   │   ├── test_jira_dc_tools.py      # Jira Data Center tests
│   │   ├── test_confluence_dc_tools.py # Confluence Data Center tests
│   │   └── test_bitbucket_dc_tools.py # Bitbucket Server tests
│   └── __init__.py
├── .gitignore                  # Git ignore rules
├── .samignore                  # SAM ignore rules
├── DEPLOYMENT_CHECKLIST.md     # Deployment guide
├── lambda_handler.py           # AWS Lambda handler (auto-detects platform)
├── LICENSE                     # MIT License
├── PHASE2_SUMMARY.md           # Phase 2 implementation details
├── PLATFORM_GUIDE.md           # Quick reference for both platforms
├── README.md                   # This file
├── requirements.txt            # Lambda dependencies
├── samconfig.toml              # SAM configuration
└── template.yaml               # SAM deployment template
```

## API Documentation

**Cloud APIs:**
- [Jira Cloud REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v2/)
- [Confluence Cloud REST API](https://developer.atlassian.com/cloud/confluence/rest/v2/)
- [Bitbucket Cloud REST API](https://developer.atlassian.com/cloud/bitbucket/rest/)

**Data Center APIs:**
- [Jira Data Center REST API](https://docs.atlassian.com/software/jira/docs/api/REST/latest/)
- [Confluence Data Center REST API](https://docs.atlassian.com/confluence/REST/latest/)
- [Bitbucket Server REST API](https://docs.atlassian.com/bitbucket-server/rest/latest/)

## License

MIT
