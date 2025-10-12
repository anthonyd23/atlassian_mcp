import asyncio
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
from .bitbucket_provider import BitbucketProvider
from .confluence_provider import ConfluenceProvider
from .jira_provider import JiraProvider

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
    return [
        Tool(
            name="search_bitbucket",
            description="Search Bitbucket repositories and pull requests",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_confluence",
            description="Search Confluence pages and spaces",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_jira",
            description="Search Jira issues using JQL",
            inputSchema={
                "type": "object",
                "properties": {
                    "jql": {"type": "string", "description": "JQL query"}
                },
                "required": ["jql"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "search_bitbucket":
        result = await bitbucket.search(arguments["query"])
    elif name == "search_confluence":
        result = await confluence.search(arguments["query"])
    elif name == "search_jira":
        result = await jira.search(arguments["jql"])
    else:
        raise ValueError(f"Unknown tool: {name}")
    
    return [TextContent(type="text", text=str(result))]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
