# Deployment Guide

## Quick Start

### For Cloud Deployment

```bash
sam deploy --guided
```

When prompted, provide credentials for the services you need:
- **AtlassianBaseUrl**: `https://yourcompany.atlassian.net`
- **AtlassianUsername**: `your-email@company.com`
- **AtlassianApiToken**: `your-api-token` (for Jira/Confluence)
- **BitbucketWorkspace**: `your-workspace` (optional)
- **BitbucketApiToken**: `your-bitbucket-token` (optional)
- Leave Data Center parameters empty

### For Data Center Deployment

```bash
sam deploy --guided
```

When prompted, provide credentials for the services you need:
- **JiraBaseUrl**: `https://jira.yourcompany.com` (optional)
- **JiraPatToken**: `your-jira-pat-token` (optional)
- **ConfluenceBaseUrl**: `https://wiki.yourcompany.com` (optional)
- **ConfluencePatToken**: `your-confluence-pat-token` (optional)
- **BitbucketBaseUrl**: `https://git.yourcompany.com` (optional)
- **BitbucketPatToken**: `your-bitbucket-pat-token` (optional)
- **BitbucketProject**: `YOUR_PROJECT_KEY` (optional)
- Leave Cloud parameters empty

## Non-Interactive Deployment

### Cloud (All Services)
```bash
sam deploy \
  --parameter-overrides \
    AtlassianBaseUrl=https://yourcompany.atlassian.net \
    AtlassianUsername=your-email@company.com \
    AtlassianApiToken=your-token \
    BitbucketWorkspace=your-workspace \
    BitbucketApiToken=your-bitbucket-token
```

### Cloud (Jira/Confluence Only)
```bash
sam deploy \
  --parameter-overrides \
    AtlassianBaseUrl=https://yourcompany.atlassian.net \
    AtlassianUsername=your-email@company.com \
    AtlassianApiToken=your-token
```

### Data Center (All Services)
```bash
sam deploy \
  --parameter-overrides \
    JiraBaseUrl=https://jira.yourcompany.com \
    JiraPatToken=your-jira-token \
    ConfluenceBaseUrl=https://wiki.yourcompany.com \
    ConfluencePatToken=your-confluence-token \
    BitbucketBaseUrl=https://git.yourcompany.com \
    BitbucketPatToken=your-bitbucket-token \
    BitbucketProject=YOUR_PROJECT_KEY
```

### Data Center (Jira Only)
```bash
sam deploy \
  --parameter-overrides \
    JiraBaseUrl=https://jira.yourcompany.com \
    JiraPatToken=your-jira-token
```

## Configuration File (samconfig.toml)

The `samconfig.toml` file stores your deployment settings. After running `sam deploy --guided` once, your choices are saved here:

```toml
version = 0.1

[default.deploy.parameters]
stack_name = "atlassian-mcp-stack"
resolve_s3 = true
s3_prefix = "atlassian-mcp-stack"
region = "us-east-1"
confirm_changeset = false
capabilities = "CAPABILITY_IAM"
parameter_overrides = "AtlassianBaseUrl=\"https://yourcompany.atlassian.net\" AtlassianUsername=\"your-email@company.com\""
```

**Note:** API tokens are NOT stored in `samconfig.toml` for security. You must provide them on each deployment via:
- Command line: `--parameter-overrides AtlassianApiToken=your-token`
- Interactive prompt: `sam deploy --guided`

After initial setup, subsequent deployments only need:
```bash
sam build && sam deploy
```

## Platform Detection

The Lambda function automatically detects the platform:
- If any service-specific PAT token is set (JIRA_PAT_TOKEN, CONFLUENCE_PAT_TOKEN, or BITBUCKET_PAT_TOKEN) → Data Center mode
- Otherwise → Cloud mode

Platform detection happens at runtime based on environment variables.
