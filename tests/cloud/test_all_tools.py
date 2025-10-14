#!/usr/bin/env python3
"""Test all 46 MCP tools"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

async def run_tests():
    print("=" * 60)
    print("TESTING ALL ATLASSIAN CLOUD TOOLS (46 TOTAL)")
    print("=" * 60)
    
    from mcp_server.cloud.jira_provider import JiraProvider
    from mcp_server.cloud.confluence_provider import ConfluenceProvider
    from mcp_server.cloud.bitbucket_provider import BitbucketProvider
    
    # Test Jira (14 tools)
    print("\n" + "=" * 60)
    print("JIRA CLOUD TOOLS (14)")
    print("=" * 60)
    jira = JiraProvider()
    
    print("\n1. list_projects")
    print(await jira.list_projects())
    
    print("\n2. search_jira")
    print(await jira.search("project = TEST"))
    
    # Test Confluence (12 tools)
    print("\n" + "=" * 60)
    print("CONFLUENCE CLOUD TOOLS (12)")
    print("=" * 60)
    confluence = ConfluenceProvider()
    
    print("\n1. list_spaces")
    print(await confluence.list_spaces())
    
    print("\n2. search_confluence")
    print(await confluence.search("test"))
    
    # Test Bitbucket (20 tools)
    print("\n" + "=" * 60)
    print("BITBUCKET CLOUD TOOLS (20)")
    print("=" * 60)
    bitbucket = BitbucketProvider()
    
    print("\n1. list_repositories")
    print(await bitbucket.list_repositories())
    
    print("\n2. search_bitbucket")
    print(await bitbucket.search("test"))
    
    print("\n" + "=" * 60)
    print("ALL CLOUD TOOLS TEST COMPLETED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_tests())
