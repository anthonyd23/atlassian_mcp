import json
import asyncio
import os
import time
import logging
import boto3
from datetime import datetime
from mcp_server.common.tools import JIRA_TOOLS, CONFLUENCE_TOOLS, BITBUCKET_TOOLS, TICKET_SUPPORT_TOOLS
from mcp_server.common.tool_schemas import TOOL_SCHEMAS
from mcp_server.common.router import route_tool_call

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

# Detect platform: Data Center uses service-specific PAT tokens, Cloud uses shared credentials
PLATFORM = 'datacenter' if (os.getenv('JIRA_PAT_TOKEN') or os.getenv('CONFLUENCE_PAT_TOKEN') or os.getenv('BITBUCKET_PAT_TOKEN')) else 'cloud'

# Initialize providers based on platform (providers handle their own availability)
if PLATFORM == 'datacenter':
    jira = JiraDCProvider()
    confluence = ConfluenceDCProvider()
    bitbucket = BitbucketDCProvider()
else:
    jira = JiraProvider()
    confluence = ConfluenceProvider()
    bitbucket = BitbucketProvider()

# Initialize ticket support agent if configured
try:
    agent_primary = os.getenv('AGENT_PRIMARY_TEAM', '')
    agent_secondary = os.getenv('AGENT_SECONDARY_TEAM', '')
    if agent_primary or agent_secondary:
        from mcp_server.common.ticket_support_tools import initialize_agent
        primary_team = json.loads(agent_primary) if agent_primary else []
        secondary_team = json.loads(agent_secondary) if agent_secondary else []
        template_mapping = json.loads(os.getenv('AGENT_TEMPLATE_MAPPING', '{}'))
        excluded_types = json.loads(os.getenv('AGENT_EXCLUDED_TYPES', '[]'))
        workload_statuses = json.loads(os.getenv('AGENT_WORKLOAD_STATUSES', '[]'))
        support_jql = os.getenv('AGENT_SUPPORT_JQL', '')
        initialize_agent(
            primary_team,
            secondary_team,
            template_mapping,
            confluence if confluence.available else None,
            excluded_types,
            workload_statuses,
            support_jql
        )
        logger.info(f"Ticket support agent initialized with {len(primary_team)} primary and {len(secondary_team)} secondary team members")
except Exception as e:
    logger.warning(f"Failed to initialize ticket support agent: {e}")

# Merge tools with their schemas
ALL_TOOLS = []
for tool in (JIRA_TOOLS + CONFLUENCE_TOOLS + BITBUCKET_TOOLS + TICKET_SUPPORT_TOOLS):
    tool_with_schema = tool.copy()
    if tool['name'] in TOOL_SCHEMAS:
        tool_with_schema['inputSchema'] = TOOL_SCHEMAS[tool['name']]
    else:
        tool_with_schema['inputSchema'] = {"type": "object", "properties": {}}
    ALL_TOOLS.append(tool_with_schema)

async def call_tool(name: str, arguments: dict):
    return await route_tool_call(name, arguments, jira, confluence, bitbucket)

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
                'body': json.dumps({'tools': ALL_TOOLS})
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