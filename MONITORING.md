# Monitoring and Alerts Guide

## CloudWatch Alarms

The following alarms are automatically created when you provide an email address during deployment:

### 1. **Error Alarm**
- **Metric**: Lambda Errors
- **Threshold**: > 5 errors in 5 minutes
- **Action**: Email alert
- **What it means**: Lambda function is failing

### 2. **Throttle Alarm**
- **Metric**: Lambda Throttles
- **Threshold**: > 10 throttles in 5 minutes
- **Action**: Email alert
- **What it means**: Too many concurrent requests, need to increase Lambda concurrency

### 3. **Duration Alarm**
- **Metric**: Lambda Duration
- **Threshold**: > 25 seconds average over 10 minutes
- **Action**: Email alert
- **What it means**: Function is slow, may timeout soon (30s limit)

### 4. **API Gateway 4xx Alarm**
- **Metric**: Client Errors (4xx)
- **Threshold**: > 20 errors in 5 minutes
- **Action**: Email alert
- **What it means**: Bad requests (likely missing/invalid API key)

### 5. **API Gateway 5xx Alarm**
- **Metric**: Server Errors (5xx)
- **Threshold**: > 1 error in 5 minutes
- **Action**: Email alert
- **What it means**: Lambda or API Gateway failure

## Setup Alerts

### During Initial Deployment
```bash
sam deploy --guided
# When prompted for AlertEmail, enter your email
# You'll receive a confirmation email - click the link to subscribe
```

### Add Alerts to Existing Deployment
```bash
sam deploy --parameter-overrides AlertEmail=your-email@example.com
```

### Remove Alerts
```bash
sam deploy --parameter-overrides AlertEmail=""
```

## View Metrics in AWS Console

### Lambda Metrics
1. Go to AWS Lambda Console
2. Select `atlassian-mcp-stack-AtlassianMCPFunction-xxx`
3. Click **Monitor** tab
4. View:
   - Invocations
   - Duration
   - Errors
   - Throttles
   - Concurrent executions

### API Gateway Metrics
1. Go to API Gateway Console
2. Select your API
3. Click **Dashboard**
4. View:
   - API calls
   - Latency
   - 4xx/5xx errors
   - Cache hits/misses

### CloudWatch Logs
```bash
# View recent logs
aws logs tail /aws/lambda/atlassian-mcp-stack-AtlassianMCPFunction-xxx --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/atlassian-mcp-stack-AtlassianMCPFunction-xxx \
  --filter-pattern "ERROR"
```

## Custom Dashboards

### Create CloudWatch Dashboard
```bash
aws cloudwatch put-dashboard --dashboard-name AtlassianMCP --dashboard-body file://dashboard.json
```

**dashboard.json:**
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/Lambda", "Invocations", {"stat": "Sum"}],
          [".", "Errors", {"stat": "Sum"}],
          [".", "Duration", {"stat": "Average"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "Lambda Performance"
      }
    }
  ]
}
```

## Cost Monitoring

### Set Budget Alert
```bash
aws budgets create-budget \
  --account-id YOUR_ACCOUNT_ID \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json
```

**budget.json:**
```json
{
  "BudgetName": "AtlassianMCP-Monthly",
  "BudgetLimit": {
    "Amount": "10",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

## Recommended Monitoring Schedule

- **Daily**: Check CloudWatch dashboard for anomalies
- **Weekly**: Review error logs and performance trends
- **Monthly**: Analyze costs and optimize if needed
- **Quarterly**: Review and rotate API tokens

## Troubleshooting Common Alerts

### High Error Rate
1. Check CloudWatch Logs for error details
2. Verify Atlassian credentials are valid
3. Check Atlassian service status
4. Test API manually with curl

### High Throttle Rate
1. Increase Lambda reserved concurrency
2. Review API Gateway rate limits
3. Check if legitimate traffic spike

### Slow Response Times
1. Check Atlassian API response times
2. Review Lambda memory allocation (increase if needed)
3. Optimize code if possible

### 4xx Errors
1. Verify API key is being sent correctly
2. Check API key hasn't been revoked
3. Review request format

### 5xx Errors
1. Check Lambda logs for exceptions
2. Verify environment variables are set
3. Test Lambda function directly
