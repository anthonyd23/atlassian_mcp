import asyncio
import os
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

# Detect platform: Data Center uses PAT token, Cloud uses API token
PLATFORM = 'datacenter' if (os.getenv('ATLASSIAN_PAT_TOKEN') or os.getenv('JIRA_PAT_TOKEN') or os.getenv('CONFLUENCE_PAT_TOKEN') or os.getenv('BITBUCKET_PAT_TOKEN')) else 'cloud'

# Initialize providers based on platform
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
