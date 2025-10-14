# Atlassian MCP Server

Model Context Protocol (MCP) server for Atlassian tools (Jira, Confluence, and Bitbucket). Works with both Atlassian Cloud and Data Center deployments.

## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Amazon Q Integration](#amazon-q-integration)
- [AWS Deployment](#aws-deployment)
- [Testing](#testing)
- [Monitoring](#monitoring)
- [Documentation](#documentation)
- [API Documentation](#api-documentation)
- [Security](#security)
- [License](#license)

## Quick Start

**Local Development:**
```bash
pip install -r mcp_server/requirements.txt
# Set credentials (see Configuration section)
python mcp_server/main.py
```

**AWS Deployment:**
```bash
sam build && sam deploy --guided
```

## Features

- **Jira**: Issues, comments, transitions, attachments, attachment upload, users, worklogs, labels, issue linking, advanced search, priority management, agile boards, sprints, user permissions
- **Confluence**: Pages, spaces, comments, attachments, search, users, labels, page history, permissions, page copying, user content, recent content, version restore, search by author/label
- **Bitbucket**: Repositories, pull requests, commits, branches, diffs, reviewers, branch management, PR activity, default reviewers, author filtering, change requests, branch restrictions, build status, webhooks
- **Flexible Credentials**: Configure only the services you need
- **Dual Platform**: Supports both Cloud and Data Center deployments
- **AWS Ready**: Deploy as Lambda function with API Gateway

## Prerequisites

- Python 3.11+
- Atlassian account (Cloud or Data Center)
- API tokens for services you want to use

**Generate Tokens:**
- Cloud: https://id.atlassian.com/manage-profile/security/api-tokens
- Bitbucket Cloud: https://bitbucket.org/account/settings/app-passwords/
- Data Center: Profile → Personal Access Tokens

## Configuration

### Cloud (Jira/Confluence)
```bash
export ATLASSIAN_BASE_URL="https://yourcompany.atlassian.net"
export ATLASSIAN_USERNAME="your-email@company.com"
export ATLASSIAN_API_TOKEN="your-token"
```

### Cloud (Bitbucket)
```bash
export BITBUCKET_WORKSPACE="your-workspace"
export BITBUCKET_API_TOKEN="your-token"
export ATLASSIAN_USERNAME="your-email@company.com"
```

### Data Center
```bash
# Per service
export JIRA_BASE_URL="https://jira.company.com"
export JIRA_PAT_TOKEN="your-token"

export CONFLUENCE_BASE_URL="https://wiki.company.com"
export CONFLUENCE_PAT_TOKEN="your-token"

export BITBUCKET_BASE_URL="https://git.company.com"
export BITBUCKET_PAT_TOKEN="your-token"
export BITBUCKET_PROJECT="PROJECT_KEY"
```

## Amazon Q Integration

Add to Amazon Q Developer settings:

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

## AWS Deployment

Deploy to Lambda with API Gateway:

```bash
sam build
sam deploy --guided
```

Retrieve API key:
```bash
aws apigateway get-api-key --api-key <API_KEY_ID> --include-value --query "value" --output text
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for platform-specific deployment instructions.

## Testing

**Unit Tests (129 tests):**
```bash
pip install -r requirements-dev.txt
pytest tests/unit/
```

**Integration Tests:**

Cloud (tests 39 of 89 tools with real credentials):
```bash
python tests/cloud/test_all_tools.py
```

Data Center (tests core tools with real credentials):
```bash
python tests/datacenter/test_all_dc_tools.py
```

**Test Coverage:**
- Unit tests: 100% of core functionality
- Integration tests: 44% of tools (39/89)
- All tests include automatic cleanup
- Verbose output shows each tool result

## Monitoring

CloudWatch integration with:
- Structured JSON logging
- Custom metrics (tool usage, duration)
- Automatic alarms (errors, throttles, slow responses)
- Dashboard for visualization

See [MONITORING.md](MONITORING.md) for setup and configuration.

## Documentation

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - AWS deployment and configuration
- [MONITORING.md](MONITORING.md) - CloudWatch setup and alerts
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and design

## API Documentation

- [Jira Cloud](https://developer.atlassian.com/cloud/jira/platform/rest/v2/)
- [Confluence Cloud](https://developer.atlassian.com/cloud/confluence/rest/v2/)
- [Bitbucket Cloud](https://developer.atlassian.com/cloud/bitbucket/rest/)
- [Jira Data Center](https://docs.atlassian.com/software/jira/docs/api/REST/latest/)
- [Confluence Data Center](https://docs.atlassian.com/confluence/REST/latest/)
- [Bitbucket Data Center](https://docs.atlassian.com/bitbucket-server/rest/latest/)

## Security

- API Gateway authentication with API keys
- Rate limiting (100 req/sec, 200 burst)
- Encrypted credentials in Lambda environment variables
- HTTPS-only traffic

## License

MIT
