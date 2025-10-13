# Atlassian MCP Server

A Model Context Protocol (MCP) server for Atlassian tools (Jira, Confluence, and Bitbucket) with 46 tools. Works with both Atlassian Cloud and Data Center/Server deployments.

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Usage](#usage)
  - [Amazon Q Integration](#amazon-q-integration)
  - [Example Workflows](#example-workflows)
- [MCP Tools (46 Total)](#mcp-tools-46-total)
  - [Jira Tools (14)](#jira-tools-14)
  - [Confluence Tools (12)](#confluence-tools-12)
  - [Bitbucket Tools (20)](#bitbucket-tools-20)
- [AWS Deployment](#aws-deployment)
- [Testing](#testing)
- [Monitoring and Alerts](#monitoring-and-alerts)
- [Security](#security)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Architecture](#architecture)
- [License](#license)

## Quick Start

**For Amazon Q Developer (Local):**

1. Install dependencies:
   ```bash
   pip install -r mcp_server/requirements.txt
   ```

2. Configure Amazon Q Developer with your Atlassian credentials (see [Amazon Q Integration](#amazon-q-integration))

3. Start using natural language commands:
   ```
   "Search for open issues in project PROJ"
   "Show me details for PROJ-123"
   "List Bitbucket repositories"
   ```

**For AWS Lambda Deployment:**

1. Deploy to AWS:
   ```bash
   sam build
   sam deploy --guided
   ```

2. Retrieve your API key:
   ```bash
   aws apigateway get-api-key --api-key <API_KEY_ID> --include-value --query "value" --output text
   ```

3. Use the API endpoint with your key

## Prerequisites

### Required:
1. **Python 3.11+**: Required for local development and testing
2. **Atlassian Account**: Cloud or Data Center/Server instance

### For Atlassian Cloud:
1. **Atlassian API Token**: Generate from https://id.atlassian.com/manage-profile/security/api-tokens
2. **Bitbucket API Token** (optional): Only if using Bitbucket tools. Generate from https://bitbucket.org/account/settings/app-passwords/

### For Atlassian Data Center/Server:
1. **Personal Access Token (PAT)**: Generate from your Atlassian instance (Profile → Personal Access Tokens)
2. **Bitbucket Server Access** (optional): Only if using Bitbucket tools. Personal Access Token from Bitbucket Server

### For AWS Deployment:
1. **AWS CLI**: Configured with appropriate permissions. Install: https://aws.amazon.com/cli/
2. **SAM CLI**: For deployment to AWS. Install: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html

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
   
   # Optional: Only if using Bitbucket Cloud tools
   export BITBUCKET_WORKSPACE="your-workspace-name"  # Found in your Bitbucket URL
   export BITBUCKET_API_TOKEN="your-bitbucket-token"  # From https://bitbucket.org/account/settings/app-passwords/
   ```
   
   **For Atlassian Data Center/Server:**
   ```bash
   # Required for Jira and Confluence Data Center
   export ATLASSIAN_BASE_URL="https://jira.yourcompany.com"
   export ATLASSIAN_PAT_TOKEN="your-personal-access-token"
   
   # Optional: Only if using Bitbucket Server tools
   export BITBUCKET_PROJECT="YOUR_PROJECT_KEY"  # Your Bitbucket project key
   ```
   
   **Platform Detection:**
   - If `ATLASSIAN_PAT_TOKEN` is set → Data Center mode
   - Otherwise → Cloud mode

3. **Use with Amazon Q Developer** (see [Usage](#usage) section)

4. **Test locally** (optional):
   
   Integration tests require real Atlassian credentials and will make actual API calls.
   
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

5. **Deploy to AWS** (optional, see [AWS Deployment](#aws-deployment) section)

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

## Usage

### Amazon Q Integration

Connect this MCP server to Amazon Q Developer for AI-powered Atlassian workflows.

**Setup:**

1. Install Python dependencies: `pip install -r mcp_server/requirements.txt`
2. Open Amazon Q Developer settings
3. Navigate to **Settings → MCP Servers → Add Server**
4. Configure the server:

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

### Example Workflows

**Jira Operations:**
```
"Search for open issues in project PROJ"
"Show me details for PROJ-123"
"Create a Jira issue in project PROJ with summary 'Fix login bug'"
"Add comment to PROJ-123: 'Working on this now'"
```

**Confluence Operations:**
```
"Find Confluence pages about deployment"
"Show me page 12345"
"Update Confluence page 12345 with new deployment instructions"
```

**Bitbucket Operations:**
```
"List Bitbucket repositories"
"Show me the diff for pull request 42 in repo my-app"
"List open pull requests in my-app repository"
```

## Testing

### Unit Tests

Run unit tests with mocked responses (no credentials required):

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all unit tests
pytest tests/unit/

# Run with coverage
pytest tests/unit/ --cov=mcp_server --cov-report=term-missing
```

### Integration Tests

Run integration tests for all 46 tools. Requires real Atlassian credentials and makes actual API calls.

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

The server deploys as a Lambda function with API Gateway. The SAM template supports both Cloud and Data Center platforms.

### Quick Deploy

```bash
sam build
sam deploy --guided
```

During deployment, you'll be prompted to:
1. Choose platform: `cloud` or `datacenter`
2. Enter credentials for your chosen platform
3. (Optional) Configure Bitbucket access
4. (Optional) Set up email alerts

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment instructions for each platform.

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

## Monitoring and Alerts

Comprehensive monitoring with structured logging, custom metrics, and CloudWatch dashboard.

### Features

- **Structured JSON Logging**: All logs include request ID, tool name, duration, and platform
- **Custom Metrics**: Track tool usage and performance in CloudWatch namespace `AtlassianMCP`
- **CloudWatch Dashboard**: Visual overview of Lambda performance, tool usage, and errors
- **Email Alerts**: Automatic notifications for errors, throttles, and slow responses

### Setup Alerts

```bash
sam deploy --parameter-overrides AlertEmail=your-email@example.com
```

### Automatic Alarms

- **Error Alarm**: > 5 errors in 5 minutes
- **Throttle Alarm**: > 10 throttles in 5 minutes  
- **Duration Alarm**: > 25 seconds average
- **4xx Alarm**: > 20 client errors in 5 minutes
- **5xx Alarm**: > 1 server error in 5 minutes

### CloudWatch Dashboard

View the dashboard in AWS Console: CloudWatch → Dashboards → AtlassianMCP

The dashboard shows:
- Lambda invocations, errors, and throttles
- Response time (average, p95, p99)
- Tool usage by name
- Tool response times
- API Gateway errors
- Recent error logs

### Custom Metrics

Available in CloudWatch namespace `AtlassianMCP`:
- `ToolInvocation` - Count of tool calls (dimensions: ToolName, Platform, Status)
- `ToolDuration` - Tool execution time in milliseconds (dimensions: ToolName, Platform)

### View Logs

```bash
# Tail logs in real-time
aws logs tail /aws/lambda/atlassian-mcp-stack-AtlassianMCPFunction-xxx --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/atlassian-mcp-stack-AtlassianMCPFunction-xxx \
  --filter-pattern "ERROR"
```

See [MONITORING.md](MONITORING.md) for complete monitoring guide.

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
3. Users configure their own Atlassian credentials during deployment

## Project Structure

```
atlassian_mcp/
├── mcp_server/
│   ├── common/
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication (Cloud & Data Center)
│   │   ├── router.py           # Shared tool routing logic
│   │   ├── tools.py            # All 46 tool definitions
│   │   ├── tool_schemas.py     # JSON schemas for tool inputs
│   │   └── validation.py       # Input validation for all tools
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
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_jira_provider.py      # Jira provider unit tests
│   │   ├── test_confluence_provider.py # Confluence provider unit tests
│   │   ├── test_bitbucket_provider.py # Bitbucket provider unit tests
│   │   ├── test_validation.py         # Validation module tests
│   │   └── test_router.py             # Router module tests
│   └── __init__.py
├── .gitignore                  # Git ignore rules
├── .samignore                  # SAM ignore rules
├── dashboard.json              # CloudWatch dashboard configuration
├── DEPLOYMENT_CHECKLIST.md     # Deployment checklist
├── DEPLOYMENT_GUIDE.md         # Platform-specific deployment guide
├── lambda_handler.py           # AWS Lambda handler (auto-detects platform)
├── LICENSE                     # MIT License
├── MONITORING.md               # Monitoring and alerts guide
├── PHASE2_SUMMARY.md           # Phase 2 implementation details
├── PLATFORM_GUIDE.md           # Quick reference for both platforms
├── pytest.ini                  # Pytest configuration
├── README.md                   # This file
├── requirements-dev.txt        # Development dependencies
├── requirements.txt            # Lambda dependencies
├── samconfig.toml              # SAM configuration
├── template.yaml               # SAM deployment template
└── VALIDATION.md               # Input validation guide
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

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system architecture, component diagrams, and request flow.

## License

MIT

---

## Additional Features

- **Input Validation**: All inputs validated before API calls with actionable error messages
- **Rate Limiting**: Automatic retry with exponential backoff for API rate limits (429 errors)
- **Request Timeouts**: 25-second timeout on all HTTP requests
- **Structured Logging**: JSON logs with request ID, tool name, duration, and platform
- **Type Hints**: Full type annotations throughout codebase

See [VALIDATION.md](VALIDATION.md) for complete validation rules.
