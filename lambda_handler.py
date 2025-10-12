import json
import asyncio
import os
import time
import logging
import boto3
from datetime import datetime
from mcp_server.common.tools import JIRA_TOOLS, CONFLUENCE_TOOLS, BITBUCKET_TOOLS

# Setup structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# CloudWatch client for custom metrics
cloudwatch = boto3.client('cloudwatch')
from mcp_server.cloud.jira_provider import JiraProvider
from mcp_server.cloud.confluence_provider import ConfluenceProvider
from mcp_server.cloud.bitbucket_provider import BitbucketProvider
from mcp_server.datacenter.jira_dc_provider import JiraDCProvider
from mcp_server.datacenter.confluence_dc_provider import ConfluenceDCProvider
from mcp_server.datacenter.bitbucket_dc_provider import BitbucketDCProvider

# Detect platform: Data Center uses PAT token, Cloud uses API token
PLATFORM = 'datacenter' if os.getenv('ATLASSIAN_PAT_TOKEN') else 'cloud'

# Initialize providers based on platform
if PLATFORM == 'datacenter':
    jira = JiraDCProvider()
    confluence = ConfluenceDCProvider()
    bitbucket = BitbucketDCProvider()
else:
    jira = JiraProvider()
    confluence = ConfluenceProvider()
    bitbucket = BitbucketProvider()

ALL_TOOLS = JIRA_TOOLS + CONFLUENCE_TOOLS + BITBUCKET_TOOLS

async def call_tool(name: str, arguments: dict):
    # Jira tools
    if name == "search_jira":
        return await jira.search(arguments["jql"])
    elif name == "get_issue":
        return await jira.get_issue(arguments["issue_key"])
    elif name == "create_issue":
        return await jira.create_issue(arguments["project_key"], arguments["summary"], arguments["description"], arguments.get("issue_type", "Task"))
    elif name == "update_issue":
        return await jira.update_issue(arguments["issue_key"], arguments["fields"])
    elif name == "add_comment":
        return await jira.add_comment(arguments["issue_key"], arguments["comment"])
    elif name == "get_issue_comments":
        return await jira.get_issue_comments(arguments["issue_key"])
    elif name == "transition_issue":
        return await jira.transition_issue(arguments["issue_key"], arguments["transition_id"])
    elif name == "get_issue_transitions":
        return await jira.get_issue_transitions(arguments["issue_key"])
    elif name == "assign_issue":
        return await jira.assign_issue(arguments["issue_key"], arguments["account_id"])
    elif name == "delete_issue":
        return await jira.delete_issue(arguments["issue_key"])
    elif name == "list_projects":
        return await jira.list_projects()
    elif name == "get_project":
        return await jira.get_project(arguments["project_key"])
    elif name == "get_issue_attachments":
        return await jira.get_issue_attachments(arguments["issue_key"])
    elif name == "get_issue_watchers":
        return await jira.get_issue_watchers(arguments["issue_key"])
    # Confluence tools
    elif name == "search_confluence":
        return await confluence.search(arguments["query"])
    elif name == "get_page":
        return await confluence.get_page(arguments["page_id"])
    elif name == "get_page_by_title":
        return await confluence.get_page_by_title(arguments["space_key"], arguments["title"])
    elif name == "create_page":
        return await confluence.create_page(arguments["space_key"], arguments["title"], arguments["content"], arguments.get("parent_id"))
    elif name == "update_page":
        return await confluence.update_page(arguments["page_id"], arguments["title"], arguments["content"], arguments["version"])
    elif name == "delete_page":
        return await confluence.delete_page(arguments["page_id"])
    elif name == "list_pages":
        return await confluence.list_pages(arguments["space_key"])
    elif name == "get_space":
        return await confluence.get_space(arguments["space_key"])
    elif name == "list_spaces":
        return await confluence.list_spaces()
    elif name == "get_page_comments":
        return await confluence.get_page_comments(arguments["page_id"])
    elif name == "add_page_comment":
        return await confluence.add_page_comment(arguments["page_id"], arguments["comment"])
    elif name == "get_page_attachments":
        return await confluence.get_page_attachments(arguments["page_id"])
    # Bitbucket tools
    elif name == "search_bitbucket":
        return await bitbucket.search(arguments["query"])
    elif name == "get_repository":
        return await bitbucket.get_repository(arguments["repo_slug"])
    elif name == "list_repositories":
        return await bitbucket.list_repositories()
    elif name == "list_pull_requests":
        return await bitbucket.list_pull_requests(arguments["repo_slug"], arguments.get("state", "OPEN"))
    elif name == "get_pull_request":
        return await bitbucket.get_pull_request(arguments["repo_slug"], arguments["pr_id"])
    elif name == "create_pull_request":
        return await bitbucket.create_pull_request(arguments["repo_slug"], arguments["title"], arguments["source_branch"], arguments["dest_branch"], arguments.get("description", ""))
    elif name == "get_file_content":
        return await bitbucket.get_file_content(arguments["repo_slug"], arguments["file_path"], arguments.get("branch", "main"))
    elif name == "list_commits":
        return await bitbucket.list_commits(arguments["repo_slug"], arguments.get("branch", "main"))
    elif name == "get_commit":
        return await bitbucket.get_commit(arguments["repo_slug"], arguments["commit_hash"])
    elif name == "list_branches":
        return await bitbucket.list_branches(arguments["repo_slug"])
    elif name == "get_pull_request_diff":
        return await bitbucket.get_pull_request_diff(arguments["repo_slug"], arguments["pr_id"])
    elif name == "get_pull_request_comments":
        return await bitbucket.get_pull_request_comments(arguments["repo_slug"], arguments["pr_id"])
    elif name == "add_pr_comment":
        return await bitbucket.add_pr_comment(arguments["repo_slug"], arguments["pr_id"], arguments["comment"])
    elif name == "approve_pull_request":
        return await bitbucket.approve_pull_request(arguments["repo_slug"], arguments["pr_id"])
    elif name == "merge_pull_request":
        return await bitbucket.merge_pull_request(arguments["repo_slug"], arguments["pr_id"])
    elif name == "get_commit_diff":
        return await bitbucket.get_commit_diff(arguments["repo_slug"], arguments["commit_hash"])
    elif name == "list_tags":
        return await bitbucket.list_tags(arguments["repo_slug"])
    elif name == "list_directory":
        return await bitbucket.list_directory(arguments["repo_slug"], arguments.get("path", ""), arguments.get("branch", "main"))
    elif name == "update_pull_request":
        return await bitbucket.update_pull_request(arguments["repo_slug"], arguments["pr_id"], arguments.get("title"), arguments.get("description"))
    elif name == "compare_commits":
        return await bitbucket.compare_commits(arguments["repo_slug"], arguments["from_commit"], arguments["to_commit"])
    else:
        raise ValueError(f"Unknown tool: {name}")

def log_structured(level, message, **kwargs):
    """Log structured JSON messages"""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'level': level,
        'message': message,
        **kwargs
    }
    logger.log(getattr(logging, level), json.dumps(log_entry))

def put_metric(metric_name, value, unit='Count', **dimensions):
    """Send custom metric to CloudWatch"""
    try:
        cloudwatch.put_metric_data(
            Namespace='AtlassianMCP',
            MetricData=[{
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow(),
                'Dimensions': [{'Name': k, 'Value': v} for k, v in dimensions.items()]
            }]
        )
    except Exception as e:
        logger.error(f"Failed to send metric: {e}")

def lambda_handler(event, context):
    """AWS Lambda handler for MCP server"""
    request_id = context.aws_request_id
    start_time = time.time()
    
    log_structured('INFO', 'Request received', 
                   request_id=request_id,
                   platform=PLATFORM,
                   http_method=event.get('httpMethod'))
    
    # Health check
    if event.get('httpMethod') == 'GET':
        log_structured('INFO', 'Health check', request_id=request_id)
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'healthy', 'tools': len(ALL_TOOLS), 'platform': PLATFORM})
        }
    
    # Parse request
    try:
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)
        
        method = body.get('method')
        params = body.get('params', {})
        
        # List tools
        if method == 'tools/list':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'tools': [{'name': t['name'], 'description': t['description']} for t in ALL_TOOLS]})
            }
        
        # Call tool
        if method == 'tools/call':
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            tool_start = time.time()
            
            log_structured('INFO', 'Tool invocation started',
                          request_id=request_id,
                          tool_name=tool_name,
                          platform=PLATFORM)
            
            # Run async tool call
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(call_tool(tool_name, arguments))
                tool_duration = (time.time() - tool_start) * 1000  # ms
                
                # Log success
                log_structured('INFO', 'Tool invocation succeeded',
                              request_id=request_id,
                              tool_name=tool_name,
                              duration_ms=tool_duration,
                              platform=PLATFORM)
                
                # Send custom metrics
                put_metric('ToolInvocation', 1, ToolName=tool_name, Platform=PLATFORM, Status='Success')
                put_metric('ToolDuration', tool_duration, unit='Milliseconds', ToolName=tool_name, Platform=PLATFORM)
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'result': result})
                }
            except Exception as tool_error:
                tool_duration = (time.time() - tool_start) * 1000
                
                # Log failure
                log_structured('ERROR', 'Tool invocation failed',
                              request_id=request_id,
                              tool_name=tool_name,
                              duration_ms=tool_duration,
                              error=str(tool_error),
                              platform=PLATFORM)
                
                # Send failure metric
                put_metric('ToolInvocation', 1, ToolName=tool_name, Platform=PLATFORM, Status='Failure')
                
                raise
            finally:
                loop.close()
        
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Invalid method'})
        }
        
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        
        log_structured('ERROR', 'Request failed',
                      request_id=request_id,
                      duration_ms=duration,
                      error=str(e),
                      platform=PLATFORM)
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
    finally:
        total_duration = (time.time() - start_time) * 1000
        log_structured('INFO', 'Request completed',
                      request_id=request_id,
                      total_duration_ms=total_duration,
                      platform=PLATFORM)