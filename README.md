# Atlassian MCP Server

[![Tests](https://github.com/anthonyd23/atlassian_mcp/actions/workflows/tests.yml/badge.svg)](https://github.com/anthonyd23/atlassian_mcp/actions/workflows/tests.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)
[![AWS SAM](https://img.shields.io/badge/AWS-SAM-orange.svg)](https://aws.amazon.com/serverless/sam/)

Model Context Protocol (MCP) server for Atlassian tools (Jira, Confluence, and Bitbucket).

> **Enterprise-grade MCP server providing 101 production-ready tools for Jira, Confluence, and Bitbucket**
> 
> - ✨ Works with Amazon Q Developer, Claude, Cursor, and more
> - 🚀 Deploy locally or to AWS Lambda
> - 🔒 Enterprise security built-in
> - 🎫 Ticket Support Agent with 6 specialized tools

## Quick Links

- 🚀 [Quick Start](#quick-start) - Get running in 5 minutes
- 📖 [Understanding MCP](docs/MCP_OVERVIEW.md) - Learn how MCP works
- 🤖 [AI Agent Setup](docs/AGENT_INTEGRATION.md) - Connect to Amazon Q, Claude, Cursor, etc.
- ☁️ [AWS Deployment](docs/DEPLOYMENT_GUIDE.md) - Deploy to Lambda
- 📊 [Monitoring](docs/MONITORING.md) - CloudWatch metrics and alerts
- 🏗️ [Architecture](docs/ARCHITECTURE.md) - System design and components

## Quick Start

**Local Development:**
```bash
pip install -r mcp_server/requirements.txt
cp config.template.yaml config.yaml
# Edit config.yaml with your credentials
python mcp_server/main.py
```

**Configuration Examples:**

Cloud:
```yaml
deployment_type: cloud
cloud:
  atlassian_base_url: https://yourcompany.atlassian.net
  atlassian_username: your-email@company.com
  atlassian_api_token: your-token
  bitbucket_workspace: your-workspace
  bitbucket_api_token: your-token
```

Data Center:
```yaml
deployment_type: datacenter
datacenter:
  jira_base_url: https://jira.company.com
  jira_pat_token: your-token
  confluence_base_url: https://wiki.company.com
  confluence_pat_token: your-token
  bitbucket_base_url: https://git.company.com
  bitbucket_pat_token: your-token
  bitbucket_project: PROJECT_KEY
```

**AWS Deployment:**
```bash
cp config.template.yaml config.yaml
# Edit config.yaml with your credentials
python deploy.py
```

## Features

- **Jira** (31 tools): Issues, comments, transitions, attachments, attachment upload, users, worklogs, labels, issue linking, advanced search, priority management, agile boards, sprints, user permissions
- **Confluence** (30 tools): Pages, spaces, comments, attachments, search, users, labels, page history, permissions, page copying, user content, recent content, version restore, search by author/label, page hierarchy (move, children, descendants, ancestors), CQL search
- **Bitbucket** (34 tools): Repositories, pull requests, commits, branches, diffs, file search, reviewers, branch management, PR activity, default reviewers, author filtering, change requests, branch restrictions, build status, webhooks
- **Ticket Support Agent** (6 tools): Open ticket triage, template validation, assignee suggestions, team workload analysis, expertise JQL construction, troubleshooting doc lookup
- **Flexible Credentials**: Configure only the services you need
- **Dual Platform**: Supports both Cloud and Data Center deployments
- **AWS Ready**: Deploy as Lambda function with API Gateway

## Prerequisites

**Local Development:**
- Python 3.11+
- Atlassian account (Cloud or Data Center)
- API tokens for services you want to use

**AWS Deployment (optional):**
- AWS CLI configured with credentials
- AWS SAM CLI installed ([installation guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))

**Generate Tokens:**
- Cloud: https://id.atlassian.com/manage-profile/security/api-tokens
- Bitbucket Cloud: https://bitbucket.org/account/settings/app-passwords/
- Data Center: Profile → Personal Access Tokens

## Configuration

### AWS Deployment

1. Copy the template:
```bash
cp config.template.yaml config.yaml
```

2. Edit `config.yaml` with your credentials:

**For Cloud:**
```yaml
deployment_type: cloud
cloud:
  atlassian_base_url: https://yourcompany.atlassian.net
  atlassian_username: your-email@company.com
  atlassian_api_token: your-token
  bitbucket_workspace: your-workspace  # optional
  bitbucket_api_token: your-token      # optional
```

**For Data Center:**
```yaml
deployment_type: datacenter
datacenter:
  jira_base_url: https://jira.company.com
  jira_pat_token: your-token
  confluence_base_url: https://wiki.company.com
  confluence_pat_token: your-token
  bitbucket_base_url: https://git.company.com
  bitbucket_pat_token: your-token
  bitbucket_project: PROJECT_KEY
```

3. Deploy:
```bash
python deploy.py
```

### Local Development

For local development, use `config.yaml` (same format as AWS deployment):

```bash
cp config.template.yaml config.yaml
# Edit config.yaml with your credentials and optional ticket support agent config
python mcp_server/main.py
```

**Note**: The server loads configuration from `config.yaml` automatically. Environment variables can be used as an alternative if `config.yaml` is not present, but using `config.yaml` is the recommended approach for consistency with AWS deployment.

**Platform Detection**: The server automatically detects whether to use Cloud or Data Center APIs in this order:
1. `DEPLOYMENT_TYPE` environment variable (`cloud` or `datacenter`)
2. `deployment_type` field in `config.yaml`
3. Presence of Data Center credentials (PAT tokens)
4. Defaults to Cloud if none of the above

## AI Agent Integration

Integrate with popular AI agents and development tools:

**Amazon Q Developer:**
```json
{
  "mcpServers": {
    "atlassian-mcp": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server/main.py"],
      "env": {
        "ATLASSIAN_BASE_URL": "https://yourcompany.atlassian.net",
        "ATLASSIAN_USERNAME": "your-email@company.com",
        "ATLASSIAN_API_TOKEN": "your-token"
      }
    }
  }
}
```

**Also supports:** Claude Desktop, Cline (VS Code), Cursor, Continue, Zed Editor

See [AGENT_INTEGRATION.md](docs/AGENT_INTEGRATION.md) for complete setup instructions.

## AWS Deployment

1. **Configure credentials:**
```bash
cp config.template.yaml config.yaml
# Edit config.yaml with your Atlassian credentials
```

2. **Deploy:**
```bash
python deploy.py
```

The script will:
- Build the SAM application
- Deploy to AWS with your credentials
- Display the MCP API URL

See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for detailed instructions.

## Testing

**Unit Tests:**
```bash
pip install -r requirements-dev.txt
pytest tests/unit/
```

**Integration Tests:**

Cloud (tests with real credentials):
```bash
python tests/cloud/test_all_cloud_tools.py
```

Data Center (tests with real credentials):
```bash
python tests/datacenter/test_all_dc_tools.py
```

Common/Agent tools (tests with real credentials):
```bash
python tests/common/test_all_common_tools.py
```

**Test Features:**
- Comprehensive unit test coverage
- Integration tests for core workflows
- Verbose output showing results

## Monitoring

CloudWatch integration with:
- Structured JSON logging
- Custom metrics (tool usage, duration)
- Automatic alarms (errors, throttles, slow responses)
- Dashboard for visualization

See [MONITORING.md](docs/MONITORING.md) for setup and configuration.

## Documentation

- [MCP_OVERVIEW.md](docs/MCP_OVERVIEW.md) - Understanding MCP and how this server works
- [AGENT_INTEGRATION.md](docs/AGENT_INTEGRATION.md) - AI agent integration (Claude, Cursor, Cline, etc.)
- [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) - AWS deployment and configuration
- [TESTING.md](docs/TESTING.md) - Comprehensive testing guide
- [TICKET_SUPPORT_AGENT.md](docs/TICKET_SUPPORT_AGENT.md) - Ticket support agent tools
- [MONITORING.md](docs/MONITORING.md) - CloudWatch setup and alerts
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture and design

## API Documentation

- [Jira Cloud](https://developer.atlassian.com/cloud/jira/platform/rest/v2/)
- [Confluence Cloud](https://developer.atlassian.com/cloud/confluence/rest/v2/)
- [Bitbucket Cloud](https://developer.atlassian.com/cloud/bitbucket/rest/)
- [Jira Data Center](https://docs.atlassian.com/software/jira/docs/api/REST/latest/)
- [Confluence Data Center](https://docs.atlassian.com/confluence/REST/latest/)
- [Bitbucket Data Center](https://docs.atlassian.com/bitbucket-server/rest/latest/)

## Security

- IAM authentication for same-account access
- Rate limiting (100 req/sec, 200 burst)
- Encrypted credentials in Lambda environment variables
- HTTPS-only traffic
- config.yaml gitignored (credentials not in version control)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on the [Model Context Protocol](https://modelcontextprotocol.io) specification
- Integrates with [Atlassian Cloud](https://www.atlassian.com/cloud) and Data Center APIs
- Designed for [Amazon Q Developer](https://aws.amazon.com/q/developer/) and other MCP-compatible AI assistants
