# Deployment Guide

## Quick Start

### For Cloud Deployment

```bash
sam deploy --guided
```

When prompted:
- **Platform**: `cloud`
- **AtlassianBaseUrl**: `https://yourcompany.atlassian.net`
- **AtlassianUsername**: `your-email@company.com`
- **AtlassianApiToken**: `your-api-token`
- **BitbucketWorkspace**: `your-workspace` (optional)
- **BitbucketApiToken**: `your-bitbucket-token` (optional)
- Leave Data Center parameters empty

### For Data Center Deployment

```bash
sam deploy --guided
```

When prompted:
- **Platform**: `datacenter`
- **AtlassianBaseUrl**: `https://jira.yourcompany.com`
- **AtlassianPatToken**: `your-personal-access-token`
- **BitbucketProject**: `YOUR_PROJECT_KEY` (optional)
- Leave Cloud parameters empty

## Non-Interactive Deployment

### Cloud
```bash
sam deploy \
  --parameter-overrides \
    Platform=cloud \
    AtlassianBaseUrl=https://yourcompany.atlassian.net \
    AtlassianUsername=your-email@company.com \
    AtlassianApiToken=your-token \
    BitbucketWorkspace=your-workspace \
    BitbucketApiToken=your-bitbucket-token
```

### Data Center
```bash
sam deploy \
  --parameter-overrides \
    Platform=datacenter \
    AtlassianBaseUrl=https://jira.yourcompany.com \
    AtlassianPatToken=your-pat-token \
    BitbucketProject=YOUR_PROJECT_KEY
```

## Platform Detection

The Lambda function automatically detects the platform:
- If `ATLASSIAN_PAT_TOKEN` is set → Data Center mode
- Otherwise → Cloud mode

The `Platform` parameter is for documentation only - actual detection happens at runtime.
