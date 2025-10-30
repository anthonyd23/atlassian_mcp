import asyncio
import os
import sys
import yaml
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def load_config_to_env():
    """Load config.yaml and set environment variables if they don't exist"""
    config_path = Path(__file__).parent.parent / 'config.yaml'
    if not config_path.exists():
        return  # No config file, use existing environment variables
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        deployment_type = config.get('deployment_type', 'cloud')
        
        if deployment_type == 'cloud':
            cloud = config.get('cloud', {})
            # Only set if not already in environment
            if not os.getenv('ATLASSIAN_BASE_URL') and cloud.get('atlassian_base_url'):
                os.environ['ATLASSIAN_BASE_URL'] = cloud['atlassian_base_url']
            if not os.getenv('ATLASSIAN_USERNAME') and cloud.get('atlassian_username'):
                os.environ['ATLASSIAN_USERNAME'] = cloud['atlassian_username']
            if not os.getenv('ATLASSIAN_API_TOKEN') and cloud.get('atlassian_api_token'):
                os.environ['ATLASSIAN_API_TOKEN'] = cloud['atlassian_api_token']
            if not os.getenv('BITBUCKET_WORKSPACE') and cloud.get('bitbucket_workspace'):
                os.environ['BITBUCKET_WORKSPACE'] = cloud['bitbucket_workspace']
            if not os.getenv('BITBUCKET_API_TOKEN') and cloud.get('bitbucket_api_token'):
                os.environ['BITBUCKET_API_TOKEN'] = cloud['bitbucket_api_token']
        
        elif deployment_type == 'datacenter':
            dc = config.get('datacenter', {})
            # Jira DC
            if not os.getenv('JIRA_BASE_URL') and dc.get('jira_base_url'):
                os.environ['JIRA_BASE_URL'] = dc['jira_base_url']
            if not os.getenv('JIRA_PAT_TOKEN') and dc.get('jira_pat_token'):
                os.environ['JIRA_PAT_TOKEN'] = dc['jira_pat_token']
            # Confluence DC
            if not os.getenv('CONFLUENCE_BASE_URL') and dc.get('confluence_base_url'):
                os.environ['CONFLUENCE_BASE_URL'] = dc['confluence_base_url']
            if not os.getenv('CONFLUENCE_PAT_TOKEN') and dc.get('confluence_pat_token'):
                os.environ['CONFLUENCE_PAT_TOKEN'] = dc['confluence_pat_token']
            # Bitbucket DC
            if not os.getenv('BITBUCKET_BASE_URL') and dc.get('bitbucket_base_url'):
                os.environ['BITBUCKET_BASE_URL'] = dc['bitbucket_base_url']
            if not os.getenv('BITBUCKET_PAT_TOKEN') and dc.get('bitbucket_pat_token'):
                os.environ['BITBUCKET_PAT_TOKEN'] = dc['bitbucket_pat_token']
            if not os.getenv('BITBUCKET_PROJECT') and dc.get('bitbucket_project'):
                os.environ['BITBUCKET_PROJECT'] = dc['bitbucket_project']
    
    except Exception as e:
        print(f"Warning: Could not load config.yaml: {e}")

# Load config before importing providers
load_config_to_env()

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
from mcp_server.cloud.bitbucket_provider import BitbucketProvider
from mcp_server.cloud.confluence_provider import ConfluenceProvider
from mcp_server.cloud.jira_provider import JiraProvider
from mcp_server.datacenter.bitbucket_dc_provider import BitbucketDCProvider
from mcp_server.datacenter.confluence_dc_provider import ConfluenceDCProvider
from mcp_server.datacenter.jira_dc_provider import JiraDCProvider
from mcp_server.common.tools import JIRA_TOOLS, CONFLUENCE_TOOLS, BITBUCKET_TOOLS
from mcp_server.common.tool_schemas import TOOL_SCHEMAS
from mcp_server.common.router import route_tool_call

server = Server("atlassian-mcp")

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

@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="atlassian://bitbucket/repositories",
            name="Bitbucket Repositories",
            description="Access to Bitbucket repositories and pull requests"
        ),
        Resource(
            uri="atlassian://confluence/spaces",
            name="Confluence Spaces",
            description="Access to Confluence spaces and pages"
        ),
        Resource(
            uri="atlassian://jira/projects",
            name="Jira Projects",
            description="Access to Jira projects and issues"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri.startswith("atlassian://bitbucket/"):
        return await bitbucket.get_resource(uri)
    elif uri.startswith("atlassian://confluence/"):
        return await confluence.get_resource(uri)
    elif uri.startswith("atlassian://jira/"):
        return await jira.get_resource(uri)
    else:
        raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def list_tools() -> list[Tool]:
    all_tools = JIRA_TOOLS + CONFLUENCE_TOOLS + BITBUCKET_TOOLS
    return [Tool(name=t["name"], description=t["description"], inputSchema=TOOL_SCHEMAS.get(t["name"], {"type": "object", "properties": {}})) for t in all_tools]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    result = await route_tool_call(name, arguments, jira, confluence, bitbucket)
    return [TextContent(type="text", text=str(result))]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
