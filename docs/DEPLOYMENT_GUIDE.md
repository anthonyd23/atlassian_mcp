# Deployment Guide

## Local Development

### Quick Start

1. **Install dependencies:**
```bash
pip install -r mcp_server/requirements.txt
```

2. **Configure credentials (choose one):**

**Option A: config.yaml**
```bash
cp config.template.yaml config.yaml
# Edit config.yaml with your credentials
```

**Option B: Environment variables**
```bash
export ATLASSIAN_BASE_URL="https://yourcompany.atlassian.net"
export ATLASSIAN_USERNAME="your-email@company.com"
export ATLASSIAN_API_TOKEN="your-token"
```

3. **Run locally:**
```bash
python mcp_server/main.py
```

### Local Configuration Examples

**Cloud (config.yaml):**
```yaml
deployment_type: cloud
cloud:
  atlassian_base_url: https://yourcompany.atlassian.net
  atlassian_username: your-email@company.com
  atlassian_api_token: your-token
  # Include these for Bitbucket functionality:
  bitbucket_workspace: your-workspace
  bitbucket_api_token: your-bitbucket-token
```

**Data Center (config.yaml):**
```yaml
deployment_type: datacenter
datacenter:
  jira_base_url: https://jira.company.com
  jira_pat_token: your-jira-token
  confluence_base_url: https://wiki.company.com
  confluence_pat_token: your-confluence-token
```

---

## AWS Deployment

### Quick Start

1. **Copy configuration template:**
```bash
cp config.template.yaml config.yaml
```

2. **Edit config.yaml:**

**For Cloud:**
```yaml
stack_name: atlassian-mcp-stack
deployment_type: cloud

cloud:
  atlassian_base_url: https://yourcompany.atlassian.net
  atlassian_username: your-email@company.com
  atlassian_api_token: your-api-token
  # Required for Bitbucket functionality:
  bitbucket_workspace: your-workspace
  bitbucket_api_token: your-bitbucket-token
```

**For Data Center:**
```yaml
stack_name: atlassian-mcp-stack
deployment_type: datacenter

datacenter:
  jira_base_url: https://jira.company.com
  jira_pat_token: your-jira-pat-token
  confluence_base_url: https://wiki.company.com
  confluence_pat_token: your-confluence-pat-token
  bitbucket_base_url: https://git.company.com
  bitbucket_pat_token: your-bitbucket-pat-token
  bitbucket_project: YOUR_PROJECT_KEY
```

3. **Deploy:**
```bash
python deploy.py
```

The script will:
- Validate your configuration
- Build the SAM application
- Deploy to AWS
- Display the MCP API URL

### VPC Deployment for Private Data Center

If your organization uses private Atlassian Data Center instances accessible only through VPN, you'll need additional AWS infrastructure:

#### Network Connectivity Requirements

**Option 1: AWS Site-to-Site VPN**
```yaml
# Additional SAM template resources needed
VPC:
  Type: AWS::EC2::VPC
  Properties:
    CidrBlock: 10.0.0.0/16

PrivateSubnet:
  Type: AWS::EC2::Subnet
  Properties:
    VpcId: !Ref VPC
    CidrBlock: 10.0.1.0/24

VPNGateway:
  Type: AWS::EC2::VpnGateway
  Properties:
    Type: ipsec.1

NATGateway:
  Type: AWS::EC2::NatGateway
  Properties:
    SubnetId: !Ref PublicSubnet
    AllocationId: !GetAtt EIPForNAT.AllocationId
```

**Option 2: AWS Direct Connect**
- Dedicated network connection between AWS and corporate data center
- Higher bandwidth and reliability than VPN
- Requires coordination with AWS and corporate networking teams

#### Lambda VPC Configuration

```yaml
AtlassianMCPFunction:
  Type: AWS::Serverless::Function
  Properties:
    # ... existing properties ...
    VpcConfig:
      SecurityGroupIds:
        - !Ref LambdaSecurityGroup
      SubnetIds:
        - !Ref PrivateSubnet
    Environment:
      Variables:
        # Data Center configuration
        JIRA_BASE_URL: https://jira.internal.company.com
        CONFLUENCE_BASE_URL: https://wiki.internal.company.com
        BITBUCKET_BASE_URL: https://git.internal.company.com
```

#### Corporate Network Requirements

Your IT team will need to configure:

1. **VPN Endpoint Configuration**
   - Accept AWS VPN connection
   - Configure BGP routing if using dynamic routing

2. **Network Routing**
   - Route AWS VPC traffic to Atlassian servers
   - Ensure return path routing is configured

3. **Firewall Rules**
   - Allow Lambda subnet (10.0.1.0/24) access to Atlassian APIs
   - Permit HTTPS (443) and HTTP (80) traffic as needed

4. **DNS Resolution**
   - Ensure internal Atlassian hostnames resolve correctly
   - Configure DNS forwarding if necessary

#### Additional Considerations

**Cost Impact:**
- NAT Gateway: ~$45/month + data processing charges
- VPN Connection: ~$36/month + data transfer
- Additional EC2 resources for VPC infrastructure

**Complexity:**
- Requires coordination between AWS and corporate IT teams
- More complex troubleshooting and monitoring
- Network connectivity dependencies

**Alternative Approach:**
For organizations with private Data Center instances, consider running the MCP server locally within your corporate network instead of AWS deployment. This leverages existing VPN infrastructure without additional AWS networking complexity.

### Deployment Validation

**Standard Deployment:**
```bash
# Test connectivity to Atlassian Cloud
curl -H "Authorization: Basic $(echo -n 'email:token' | base64)" \
  https://yourcompany.atlassian.net/rest/api/2/myself
```

**VPC Deployment:**
```bash
# Test from within VPC (requires bastion host or VPC endpoints)
aws lambda invoke --function-name atlassian-mcp-function \
  --payload '{"test": "connectivity"}' response.json
```

## AWS Configuration Examples

### Cloud - Jira and Confluence Only
```yaml
deployment_type: cloud
cloud:
  atlassian_base_url: https://yourcompany.atlassian.net
  atlassian_username: your-email@company.com
  atlassian_api_token: your-token
  # Bitbucket tools will be unavailable without these credentials:
  # bitbucket_workspace: your-workspace
  # bitbucket_api_token: your-token
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

**Local Development:**
- Edit `config.yaml` or environment variables
- Restart `python mcp_server/main.py`

**AWS Deployment:**
- Edit `config.yaml`
- Run `python deploy.py`
- Updates Lambda environment variables

## Security Notes

- `config.yaml` is gitignored - safe to store credentials locally
- **Local:** Credentials loaded into process environment
- **AWS:** Credentials encrypted at rest in Lambda
- Never commit `config.yaml` to version control

## Platform Detection

Both local and AWS modes detect platform based on configuration priority:

1. **DEPLOYMENT_TYPE environment variable** (highest priority)
2. **deployment_type in config.yaml**
3. **Data Center credentials detection** (presence of PAT tokens)
4. **Default to Cloud** (lowest priority)

**Cloud mode:** Uses `ATLASSIAN_API_TOKEN` + `ATLASSIAN_USERNAME`
**Data Center mode:** Uses service-specific PAT tokens (`JIRA_PAT_TOKEN`, etc.)

## Ticket Support Agent Configuration (Optional)

The ticket support agent provides 4 specialized tools for intelligent ticket management. Configuration is optional - if not provided, the agent tools will be listed but return errors when called.

### Configuration Structure

```yaml
ticket_support_agent:
  # Team members (Cloud: account IDs, DC: usernames)
  primary_team_members:
    - account_id: "712020:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      name: "Alice Smith"
    - account_id: "712020:yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
      name: "Bob Jones"
  
  secondary_team_members:
    - account_id: "712020:zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz"
      name: "Charlie Brown"
  
  # Issue types to exclude from workload calculation
  excluded_issue_types:
    - "Epic"
    - "Initiative"
  
  # Statuses to count in workload (optional)
  workload_statuses:
    - "Open"
    - "In Progress"
    - "Blocked"
  
  # Template mapping for ticket validation
  template_mapping:
    "Support Request":
      parent_page: "Support Request Templates"  # Confluence page title or ID
      custom_field: "customfield_10001"  # Custom field with ticket type
  
  # JQL query to find unassigned tickets
  support_jql: 'assignee is EMPTY AND status = Open ORDER BY created DESC'
```

### Platform-Specific Team Configuration

**Cloud (Account IDs):**
```yaml
primary_team_members:
  - account_id: "712020:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    name: "Alice"
```

**Data Center (Usernames):**
```yaml
primary_team_members:
  - account_id: "asmith"
    name: "Alice"
```

### Agent Tools

1. **get_open_support_tickets**: Retrieve and categorize unassigned tickets
2. **check_ticket_template**: Validate ticket completeness against templates
3. **suggest_assignee**: Recommend optimal assignee based on workload
4. **get_team_workload**: Get current workload for all team members

See [TICKET_SUPPORT_AGENT.md](TICKET_SUPPORT_AGENT.md) for detailed documentation.

### AWS Deployment with Agent

The agent configuration is automatically deployed to Lambda:

```bash
# 1. Configure in config.yaml
ticket_support_agent:
  primary_team_members: [...]
  # ... rest of config

# 2. Deploy
python deploy.py

# 3. Agent automatically initialized in Lambda
```

Configuration is passed as JSON-encoded environment variables:
- `AGENT_PRIMARY_TEAM`
- `AGENT_SECONDARY_TEAM`
- `AGENT_TEMPLATE_MAPPING`
- `AGENT_EXCLUDED_TYPES`
- `AGENT_WORKLOAD_STATUSES`
- `AGENT_SUPPORT_JQL`
