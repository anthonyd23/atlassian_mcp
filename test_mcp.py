#!/usr/bin/env python3
import asyncio
import os
from mcp_server.bitbucket_provider import BitbucketProvider
from mcp_server.confluence_provider import ConfluenceProvider
from mcp_server.jira_provider import JiraProvider

async def test_mcp_server():
    print("Testing Atlassian MCP Server...\n")
    
    if not all([os.getenv('ATLASSIAN_BASE_URL'), 
                os.getenv('ATLASSIAN_USERNAME'), 
                os.getenv('ATLASSIAN_API_TOKEN')]):
        print("Missing credentials. Set:")
        print("  ATLASSIAN_BASE_URL")
        print("  ATLASSIAN_USERNAME")
        print("  ATLASSIAN_API_TOKEN")
        return
    
    # Test Jira
    print("1. Testing Jira...")
    try:
        jira = JiraProvider()
        result = await jira.search("project is not empty")
        print(f"   Result: {result}\n")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # Test Confluence
    print("2. Testing Confluence...")
    try:
        confluence = ConfluenceProvider()
        result = await confluence.search("test")
        print(f"   Result: {result}\n")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # Test Bitbucket
    print("3. Testing Bitbucket...")
    try:
        bitbucket = BitbucketProvider()
        result = await bitbucket.search("test")
        print(f"   Result: {result}\n")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
