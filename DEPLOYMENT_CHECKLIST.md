# Deployment Checklist

## Pre-Deployment

### 1. Choose Your Platform
- [ ] Atlassian Cloud
- [ ] Atlassian Data Center/Server

### 2. Gather Credentials

#### For Cloud:
- [ ] Atlassian Cloud URL (e.g., https://yourcompany.atlassian.net)
- [ ] Atlassian email address
- [ ] Atlassian API token (from https://id.atlassian.com/manage-profile/security/api-tokens)
- [ ] Bitbucket workspace name (optional)
- [ ] Bitbucket API token (optional, from https://bitbucket.org/account/settings/app-passwords/)

#### For Data Center:
- [ ] Data Center URL (e.g., https://jira.yourcompany.com)
- [ ] Personal Access Token (from your instance profile)
- [ ] Bitbucket project key (optional)

### 3. Local Testing

#### Cloud Testing:
```bash
# Set environment variables
export ATLASSIAN_BASE_URL="https://yourcompany.atlassian.net"
export ATLASSIAN_USERNAME="your-email@company.com"
export ATLASSIAN_API_TOKEN="your-api-token"

# Run tests
python tests/cloud/test_all_tools.py
```

#### Data Center Testing:
```bash
# Set environment variables
export ATLASSIAN_BASE_URL="https://jira.yourcompany.com"
export ATLASSIAN_PAT_TOKEN="your-pat-token"

# Run tests
python tests/datacenter/test_all_dc_tools.py
```

- [ ] All tests pass locally

## AWS Deployment

### 4. AWS Prerequisites
- [ ] AWS CLI installed and configured
- [ ] SAM CLI installed
- [ ] AWS credentials configured (`aws configure`)
- [ ] Appropriate IAM permissions for Lambda and API Gateway

### 5. Build and Deploy

```bash
# Build the Lambda package
sam build

# Deploy (first time - guided)
sam deploy --guided

# Follow prompts:
# - Stack name: atlassian-mcp-server
# - AWS Region: us-east-1 (or your preferred region)
# - Confirm changes: Y
# - Allow SAM CLI IAM role creation: Y
# - Save arguments to config: Y
```

- [ ] Build completed successfully
- [ ] Deployment completed successfully
- [ ] Note the API Gateway URL from output

### 6. Configure Lambda Environment Variables

In AWS Console → Lambda → Your function → Configuration → Environment variables:

#### For Cloud:
- [ ] ATLASSIAN_BASE_URL
- [ ] ATLASSIAN_USERNAME
- [ ] ATLASSIAN_API_TOKEN
- [ ] BITBUCKET_WORKSPACE (optional)
- [ ] BITBUCKET_API_TOKEN (optional)

#### For Data Center:
- [ ] ATLASSIAN_BASE_URL
- [ ] ATLASSIAN_PAT_TOKEN
- [ ] BITBUCKET_PROJECT (optional)

### 7. Test Deployment

```bash
# Test health check
curl https://YOUR-API-URL/Prod/mcp

# Expected response:
# {"status": "healthy", "tools": 46, "platform": "cloud"}
# or
# {"status": "healthy", "tools": 46, "platform": "datacenter"}
```

- [ ] Health check returns 200 OK
- [ ] Correct platform detected
- [ ] Tool count is 46

### 8. Test MCP Tools

```bash
# Test listing tools
curl -X POST https://YOUR-API-URL/Prod/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list", "params": {}}'

# Test a specific tool (e.g., list_projects)
curl -X POST https://YOUR-API-URL/Prod/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "list_projects", "arguments": {}}}'
```

- [ ] Tools list returns all 46 tools
- [ ] Sample tool call works correctly

## Post-Deployment

### 9. Documentation
- [ ] Update API Gateway URL in your documentation
- [ ] Share endpoint with team members
- [ ] Document which platform is deployed (Cloud or Data Center)

### 10. Monitoring
- [ ] Check CloudWatch Logs for any errors
- [ ] Set up email alerts: `sam deploy --parameter-overrides AlertEmail=your-email@example.com`
- [ ] Confirm SNS subscription email
- [ ] Enable detailed API Gateway metrics (for 4xx/5xx alarms)
- [ ] View CloudWatch dashboard: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=AtlassianMCP
- [ ] Verify custom metrics appearing in namespace `AtlassianMCP`

### 11. Security Review
- [ ] Verify environment variables are encrypted
- [ ] Confirm no credentials in code or logs
- [ ] Review IAM roles and permissions
- [ ] Consider API Gateway authentication (optional)

## Troubleshooting

### Common Issues

**"Authentication failed" in Lambda logs:**
- Check environment variables are set correctly
- Verify tokens haven't expired
- Confirm base URL is correct

**"Wrong platform detected":**
- Cloud mode: Ensure ATLASSIAN_PAT_TOKEN is NOT set
- Data Center mode: Ensure ATLASSIAN_PAT_TOKEN IS set

**"Timeout errors":**
- Increase Lambda timeout (default: 3s, recommended: 30s)
- Check network connectivity to Atlassian instance

**"Module not found" errors:**
- Run `sam build` again
- Check requirements.txt includes all dependencies

## Rollback Plan

If deployment fails:
```bash
# Delete the stack
aws cloudformation delete-stack --stack-name atlassian-mcp-server

# Or rollback to previous version
sam deploy --no-confirm-changeset
```

## Update Deployment

To update after code changes:
```bash
# Rebuild and deploy
sam build
sam deploy

# No need for --guided on subsequent deploys
```

## Success Criteria

- [x] Local tests pass
- [x] AWS deployment successful
- [x] Health check returns 200
- [x] Correct platform detected
- [x] All 46 tools accessible
- [x] Sample tool calls work
- [x] No errors in CloudWatch logs
- [x] Environment variables configured
- [x] Documentation updated

## Next Steps

1. Integrate with your MCP client
2. Set up monitoring and alerts
3. Consider adding API Gateway authentication
4. Plan for token rotation
5. Document usage patterns for your team
