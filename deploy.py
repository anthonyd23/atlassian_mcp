#!/usr/bin/env python3
"""Deployment script for Atlassian MCP Server"""

import subprocess
import sys
import os
import yaml

def load_config():
    """Load configuration from config.yaml"""
    if not os.path.exists('config.yaml'):
        print("Error: config.yaml not found!")
        print("Please copy config.template.yaml to config.yaml and fill in your values.")
        sys.exit(1)
    
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def validate_config(config):
    """Validate configuration"""
    deployment_type = config.get('deployment_type', 'cloud')
    
    if deployment_type not in ['cloud', 'datacenter']:
        print("Error: deployment_type must be 'cloud' or 'datacenter'")
        return False
    
    if deployment_type == 'cloud':
        cloud = config.get('cloud', {})
        required = ['atlassian_base_url', 'atlassian_username', 'atlassian_api_token']
        for field in required:
            if not cloud.get(field) or 'your-' in cloud.get(field, ''):
                print(f"Error: Please set cloud.{field} in config.yaml")
                return False
    
    elif deployment_type == 'datacenter':
        dc = config.get('datacenter', {})
        # At least one service must be configured
        has_jira = dc.get('jira_base_url') and dc.get('jira_pat_token')
        has_confluence = dc.get('confluence_base_url') and dc.get('confluence_pat_token')
        has_bitbucket = dc.get('bitbucket_base_url') and dc.get('bitbucket_pat_token')
        
        if not (has_jira or has_confluence or has_bitbucket):
            print("Error: At least one Data Center service must be configured")
            return False
    
    return True

def build_parameter_overrides(config):
    """Build CloudFormation parameter overrides from config"""
    deployment_type = config.get('deployment_type', 'cloud')
    params = []
    
    if deployment_type == 'cloud':
        cloud = config.get('cloud', {})
        params.append(f'AtlassianBaseUrl="{cloud.get("atlassian_base_url", "")}"')
        params.append(f'AtlassianUsername="{cloud.get("atlassian_username", "")}"')
        params.append(f'AtlassianApiToken="{cloud.get("atlassian_api_token", "")}"')
        params.append(f'BitbucketWorkspace="{cloud.get("bitbucket_workspace", "")}"')
        params.append(f'BitbucketApiToken="{cloud.get("bitbucket_api_token", "")}"')
    
    elif deployment_type == 'datacenter':
        dc = config.get('datacenter', {})
        params.append(f'JiraBaseUrl="{dc.get("jira_base_url", "")}"')
        params.append(f'JiraPatToken="{dc.get("jira_pat_token", "")}"')
        params.append(f'ConfluenceBaseUrl="{dc.get("confluence_base_url", "")}"')
        params.append(f'ConfluencePatToken="{dc.get("confluence_pat_token", "")}"')
        params.append(f'BitbucketBaseUrl="{dc.get("bitbucket_base_url", "")}"')
        params.append(f'BitbucketPatToken="{dc.get("bitbucket_pat_token", "")}"')
        params.append(f'BitbucketProject="{dc.get("bitbucket_project", "")}"')
    
    # Monitoring
    alert_email = config.get('monitoring', {}).get('alert_email', '')
    params.append(f'AlertEmail="{alert_email}"')
    
    # Ticket Support Agent
    agent = config.get('ticket_support_agent', {})
    import json
    params.append(f'AgentPrimaryTeam="{json.dumps(agent.get("primary_team_members", []))}"')
    params.append(f'AgentSecondaryTeam="{json.dumps(agent.get("secondary_team_members", []))}"')
    params.append(f'AgentTemplateMapping="{json.dumps(agent.get("template_mapping", {}))}"')
    params.append(f'AgentExcludedTypes="{json.dumps(agent.get("excluded_issue_types", []))}"')
    params.append(f'AgentWorkloadStatuses="{json.dumps(agent.get("workload_statuses", []))}"')
    params.append(f'AgentSupportJql="{agent.get("support_jql", "")}"')
    
    return ' '.join(params)

def main():
    print("\n=== Atlassian MCP Server Deployment ===\n")
    
    # Load and validate config
    config = load_config()
    
    if not validate_config(config):
        sys.exit(1)
    
    stack_name = config.get('stack_name', 'atlassian-mcp-stack')
    deployment_type = config.get('deployment_type', 'cloud')
    
    print(f"Stack name: {stack_name}")
    print(f"Deployment type: {deployment_type}")
    print()
    
    # Build
    print("Building SAM application...")
    result = subprocess.run(['sam', 'build'], cwd='.')
    if result.returncode != 0:
        print("Build failed!")
        sys.exit(1)
    
    print("\nBuild succeeded!\n")
    
    # Deploy
    print("Deploying to AWS...")
    parameter_overrides = build_parameter_overrides(config)
    
    deploy_cmd = [
        'sam', 'deploy',
        '--stack-name', stack_name,
        '--parameter-overrides', parameter_overrides,
        '--capabilities', 'CAPABILITY_IAM',
        '--resolve-s3',
        '--no-confirm-changeset'
    ]
    
    result = subprocess.run(deploy_cmd, cwd='.')
    if result.returncode != 0:
        print("\nDeployment failed!")
        sys.exit(1)
    
    print("\n=== Deployment Successful! ===\n")
    
    # Get outputs
    print("Retrieving stack outputs...")
    result = subprocess.run(
        ['aws', 'cloudformation', 'describe-stacks', '--stack-name', stack_name,
         '--query', 'Stacks[0].Outputs', '--output', 'json'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        import json
        outputs = json.loads(result.stdout)
        
        print("\nStack Outputs:")
        for output in outputs:
            print(f"  {output['OutputKey']}: {output['OutputValue']}")
        
        # Get API URL
        api_url = next((o['OutputValue'] for o in outputs if o['OutputKey'] == 'MCPApiUrl'), None)
        if api_url:
            print(f"\nMCP Server URL: {api_url}")
            print("\nTo integrate with an MCP client, add this configuration:")
            print(f"  mcp_servers:")
            print(f"    - id: atlassian")
            print(f"      url: {api_url}")
            print(f"      auth_type: iam")

if __name__ == '__main__':
    main()
