# Deployment Guide

## Quick Start

### 1. Copy Configuration Template

```bash
cp config.template.yaml config.yaml
```

### 2. Edit config.yaml

**For Cloud Deployment:**
```yaml
stack_name: atlassian-mcp-stack
deployment_type: cloud

cloud:
  atlassian_base_url: https://yourcompany.atlassian.net
  atlassian_username: your-email@company.com
  atlassian_api_token: your-api-token
  
  # Bitbucket Cloud (optional)
  bitbucket_workspace: your-workspace
  bitbucket_api_token: your-bitbucket-token
```

**For Data Center Deployment:**
```yaml
stack_name: atlassian-mcp-stack
deployment_type: datacenter

datacenter:
  # Configure only the services you need
  jira_base_url: https://jira.company.com
  jira_pat_token: your-jira-pat-token
  
  confluence_base_url: https://wiki.company.com
  confluence_pat_token: your-confluence-pat-token
  
  bitbucket_base_url: https://git.company.com
  bitbucket_pat_token: your-bitbucket-pat-token
  bitbucket_project: YOUR_PROJECT_KEY
```

### 3. Deploy

```bash
python deploy.py
```

The script will:
- Validate your configuration
- Build the SAM application
- Deploy to AWS
- Display the MCP API URL

## Configuration Examples

### Cloud - Jira and Confluence Only
```yaml
deployment_type: cloud
cloud:
  atlassian_base_url: https://yourcompany.atlassian.net
  atlassian_username: your-email@company.com
  atlassian_api_token: your-token
  bitbucket_workspace: ""  # Leave empty if not using
  bitbucket_api_token: ""
```

### Cloud - All Services
```yaml
deployment_type: cloud
cloud:
  atlassian_base_url: https://yourcompany.atlassian.net
  atlassian_username: your-email@company.com
  atlassian_api_token: your-token
  bitbucket_workspace: your-workspace
  bitbucket_api_token: your-bitbucket-token
```

### Data Center - Jira Only
```yaml
deployment_type: datacenter
datacenter:
  jira_base_url: https://jira.company.com
  jira_pat_token: your-token
  confluence_base_url: ""
  confluence_pat_token: ""
  bitbucket_base_url: ""
  bitbucket_pat_token: ""
  bitbucket_project: ""
```

### Data Center - All Services
```yaml
deployment_type: datacenter
datacenter:
  jira_base_url: https://jira.company.com
  jira_pat_token: your-jira-token
  confluence_base_url: https://wiki.company.com
  confluence_pat_token: your-confluence-token
  bitbucket_base_url: https://git.company.com
  bitbucket_pat_token: your-bitbucket-token
  bitbucket_project: YOUR_PROJECT_KEY
```

## Updating Configuration

To update credentials or settings:

1. Edit `config.yaml`
2. Run `python deploy.py`

The deployment script will update the Lambda environment variables with your new configuration.

## Security Notes

- `config.yaml` is gitignored - safe to store credentials locally
- Credentials are passed to CloudFormation as parameters
- Lambda environment variables are encrypted at rest
- Never commit `config.yaml` to version control

## Platform Detection

The Lambda function automatically detects the platform based on `deployment_type` in config.yaml:
- `deployment_type: cloud` → Uses Cloud credentials (ATLASSIAN_API_TOKEN)
- `deployment_type: datacenter` → Uses Data Center credentials (PAT tokens)

Platform detection happens at runtime based on Lambda environment variables set during deployment.
