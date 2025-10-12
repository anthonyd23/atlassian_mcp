# Platform Quick Reference Guide

## Which Platform Am I Using?

### Atlassian Cloud
- URL format: `https://yourcompany.atlassian.net`
- You log in with your email address
- You create API tokens at: https://id.atlassian.com/manage-profile/security/api-tokens
- Bitbucket Cloud URL: `https://bitbucket.org/yourworkspace`

### Atlassian Data Center/Server
- URL format: `https://jira.yourcompany.com` or `http://internal-server:8080`
- Self-hosted on your company's infrastructure
- You create Personal Access Tokens in your profile settings
- Bitbucket Server URL: `https://bitbucket.yourcompany.com`

## Setup Instructions

### Cloud Setup (3 steps)
```bash
# 1. Set your Cloud instance URL
export ATLASSIAN_BASE_URL="https://yourcompany.atlassian.net"

# 2. Set your email and API token
export ATLASSIAN_USERNAME="your-email@company.com"
export ATLASSIAN_API_TOKEN="your-api-token-here"

# 3. (Optional) For Bitbucket Cloud
export BITBUCKET_WORKSPACE="your-workspace"
export BITBUCKET_API_TOKEN="your-bitbucket-token"
```

### Data Center Setup (2 steps)
```bash
# 1. Set your Data Center instance URL
export ATLASSIAN_BASE_URL="https://jira.yourcompany.com"

# 2. Set your Personal Access Token
export ATLASSIAN_PAT_TOKEN="your-pat-token-here"

# 3. (Optional) For Bitbucket Server
export BITBUCKET_PROJECT="YOUR_PROJECT_KEY"
```

## How to Get Tokens

### Cloud API Token
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a label (e.g., "MCP Server")
4. Copy the token immediately (you won't see it again)

### Cloud Bitbucket Token
1. Go to https://bitbucket.org/account/settings/app-passwords/
2. Click "Create app password"
3. Give it a label and select permissions: Repositories (Read/Write)
4. Copy the token

### Data Center Personal Access Token
1. Log into your Jira/Confluence instance
2. Click your profile picture → Profile
3. Go to "Personal Access Tokens"
4. Click "Create token"
5. Set name and expiration
6. Copy the token immediately

## Testing Your Setup

### Test Cloud
```bash
python tests/cloud/test_all_tools.py
```

### Test Data Center
```bash
python tests/datacenter/test_all_dc_tools.py
```

## Common Issues

### "Authentication failed"
- **Cloud**: Check your ATLASSIAN_USERNAME and ATLASSIAN_API_TOKEN
- **Data Center**: Check your ATLASSIAN_PAT_TOKEN

### "Wrong platform detected"
- The system detects platform based on ATLASSIAN_PAT_TOKEN
- If set → Data Center mode
- If not set → Cloud mode

### "Cannot connect to Bitbucket"
- **Cloud**: Ensure BITBUCKET_WORKSPACE and BITBUCKET_API_TOKEN are set
- **Server**: Ensure BITBUCKET_PROJECT is set and matches your project key

## API Differences

| Feature | Cloud | Data Center |
|---------|-------|-------------|
| Authentication | Basic (username:token) | Bearer (PAT) |
| Jira API | REST v2 | REST v2 |
| Confluence API | REST v2 | REST v1 |
| Bitbucket API | Cloud API 2.0 | Server API 1.0 |
| User IDs | Account IDs | Usernames |
| Workspace/Project | Workspace | Project Key |

## Quick Commands

```bash
# Check which platform Lambda is using
curl https://your-lambda-url.amazonaws.com/Prod/mcp

# Response includes: {"status": "healthy", "tools": 46, "platform": "cloud"}

# Switch from Cloud to Data Center
unset ATLASSIAN_USERNAME ATLASSIAN_API_TOKEN
export ATLASSIAN_PAT_TOKEN="your-pat-token"

# Switch from Data Center to Cloud
unset ATLASSIAN_PAT_TOKEN
export ATLASSIAN_USERNAME="your-email@company.com"
export ATLASSIAN_API_TOKEN="your-api-token"
```

## Need Help?

1. Check README.md for detailed documentation
2. Review PHASE2_SUMMARY.md for implementation details
3. Look at test files for usage examples
4. Verify environment variables are set correctly
