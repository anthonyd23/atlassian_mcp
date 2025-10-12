#!/usr/bin/env python3
import asyncio
import os
from mcp_server.jira_provider import JiraProvider
from mcp_server.confluence_provider import ConfluenceProvider
from mcp_server.bitbucket_provider import BitbucketProvider

async def quick_test():
    # Test Jira
    jira = JiraProvider()
    result = await jira.search("project is not empty")
    print("Jira test:", result)
    
    # Test Confluence  
    confluence = ConfluenceProvider()
    result = await confluence.search("test")
    print("Confluence test:", result)
    
    # Test Bitbucket
    bitbucket = BitbucketProvider()
    result = await bitbucket.search("test")
    print("Bitbucket test:", result)

if __name__ == "__main__":
    asyncio.run(quick_test())