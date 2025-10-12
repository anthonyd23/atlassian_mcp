import asyncio
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
from .cloud.bitbucket_provider import BitbucketProvider
from .cloud.confluence_provider import ConfluenceProvider
from .cloud.jira_provider import JiraProvider
from .common.tools import JIRA_TOOLS, CONFLUENCE_TOOLS, BITBUCKET_TOOLS

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
    # Jira tools
    if name == "search_jira":
        result = await jira.search(arguments["jql"])
    elif name == "get_issue":
        result = await jira.get_issue(arguments["issue_key"])
    elif name == "create_issue":
        result = await jira.create_issue(arguments["project_key"], arguments["summary"], arguments["description"], arguments.get("issue_type", "Task"))
    elif name == "update_issue":
        result = await jira.update_issue(arguments["issue_key"], arguments["fields"])
    elif name == "add_comment":
        result = await jira.add_comment(arguments["issue_key"], arguments["comment"])
    elif name == "get_issue_comments":
        result = await jira.get_issue_comments(arguments["issue_key"])
    elif name == "transition_issue":
        result = await jira.transition_issue(arguments["issue_key"], arguments["transition_id"])
    elif name == "get_issue_transitions":
        result = await jira.get_issue_transitions(arguments["issue_key"])
    elif name == "assign_issue":
        result = await jira.assign_issue(arguments["issue_key"], arguments["account_id"])
    elif name == "delete_issue":
        result = await jira.delete_issue(arguments["issue_key"])
    elif name == "list_projects":
        result = await jira.list_projects()
    elif name == "get_project":
        result = await jira.get_project(arguments["project_key"])
    # Confluence tools
    elif name == "search_confluence":
        result = await confluence.search(arguments["query"])
    elif name == "get_page":
        result = await confluence.get_page(arguments["page_id"])
    elif name == "get_page_by_title":
        result = await confluence.get_page_by_title(arguments["space_key"], arguments["title"])
    elif name == "create_page":
        result = await confluence.create_page(arguments["space_key"], arguments["title"], arguments["content"], arguments.get("parent_id"))
    elif name == "update_page":
        result = await confluence.update_page(arguments["page_id"], arguments["title"], arguments["content"], arguments["version"])
    elif name == "delete_page":
        result = await confluence.delete_page(arguments["page_id"])
    elif name == "list_pages":
        result = await confluence.list_pages(arguments["space_key"])
    elif name == "get_space":
        result = await confluence.get_space(arguments["space_key"])
    elif name == "list_spaces":
        result = await confluence.list_spaces()
    # Bitbucket tools
    elif name == "search_bitbucket":
        result = await bitbucket.search(arguments["query"])
    elif name == "get_repository":
        result = await bitbucket.get_repository(arguments["repo_slug"])
    elif name == "list_repositories":
        result = await bitbucket.list_repositories()
    elif name == "list_pull_requests":
        result = await bitbucket.list_pull_requests(arguments["repo_slug"], arguments.get("state", "OPEN"))
    elif name == "get_pull_request":
        result = await bitbucket.get_pull_request(arguments["repo_slug"], arguments["pr_id"])
    elif name == "create_pull_request":
        result = await bitbucket.create_pull_request(arguments["repo_slug"], arguments["title"], arguments["source_branch"], arguments["dest_branch"], arguments.get("description", ""))
    elif name == "get_file_content":
        result = await bitbucket.get_file_content(arguments["repo_slug"], arguments["file_path"], arguments.get("branch", "main"))
    elif name == "list_commits":
        result = await bitbucket.list_commits(arguments["repo_slug"], arguments.get("branch", "main"))
    elif name == "get_commit":
        result = await bitbucket.get_commit(arguments["repo_slug"], arguments["commit_hash"])
    elif name == "list_branches":
        result = await bitbucket.list_branches(arguments["repo_slug"])
    elif name == "get_issue_attachments":
        result = await jira.get_issue_attachments(arguments["issue_key"])
    elif name == "get_issue_watchers":
        result = await jira.get_issue_watchers(arguments["issue_key"])
    elif name == "get_page_comments":
        result = await confluence.get_page_comments(arguments["page_id"])
    elif name == "add_page_comment":
        result = await confluence.add_page_comment(arguments["page_id"], arguments["comment"])
    elif name == "get_page_attachments":
        result = await confluence.get_page_attachments(arguments["page_id"])
    elif name == "get_pull_request_diff":
        result = await bitbucket.get_pull_request_diff(arguments["repo_slug"], arguments["pr_id"])
    elif name == "get_pull_request_comments":
        result = await bitbucket.get_pull_request_comments(arguments["repo_slug"], arguments["pr_id"])
    elif name == "add_pr_comment":
        result = await bitbucket.add_pr_comment(arguments["repo_slug"], arguments["pr_id"], arguments["comment"])
    elif name == "approve_pull_request":
        result = await bitbucket.approve_pull_request(arguments["repo_slug"], arguments["pr_id"])
    elif name == "merge_pull_request":
        result = await bitbucket.merge_pull_request(arguments["repo_slug"], arguments["pr_id"])
    elif name == "get_commit_diff":
        result = await bitbucket.get_commit_diff(arguments["repo_slug"], arguments["commit_hash"])
    elif name == "list_tags":
        result = await bitbucket.list_tags(arguments["repo_slug"])
    elif name == "list_directory":
        result = await bitbucket.list_directory(arguments["repo_slug"], arguments.get("path", ""), arguments.get("branch", "main"))
    elif name == "update_pull_request":
        result = await bitbucket.update_pull_request(arguments["repo_slug"], arguments["pr_id"], arguments.get("title"), arguments.get("description"))
    elif name == "compare_commits":
        result = await bitbucket.compare_commits(arguments["repo_slug"], arguments["from_commit"], arguments["to_commit"])
    else:
        raise ValueError(f"Unknown tool: {name}")
    
    return [TextContent(type="text", text=str(result))]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
