import asyncio
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
from .cloud.bitbucket_provider import BitbucketProvider
from .cloud.confluence_provider import ConfluenceProvider
from .cloud.jira_provider import JiraProvider
from .common.tools import JIRA_TOOLS, CONFLUENCE_TOOLS, BITBUCKET_TOOLS
from .common.router import route_tool_call

server = Server("atlassian-mcp")

# Initialize providers
bitbucket = BitbucketProvider()
confluence = ConfluenceProvider()
jira = JiraProvider()

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
    return JIRA_TOOLS + CONFLUENCE_TOOLS + BITBUCKET_TOOLS

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    result = await route_tool_call(name, arguments, jira, confluence, bitbucket)
    return [TextContent(type="text", text=str(result))]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
