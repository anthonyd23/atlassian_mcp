#!/usr/bin/env python3
"""
Test script for Atlassian MCP Server
"""

import asyncio
import json
import os
from mcp_server.main import server

async def test_mcp_server():
    """Test the MCP server functionality"""
    
    print("Testing Atlassian MCP Server...")
    
    # Test list resources
    print("\n1. Testing list_resources...")
    try:
        resources = await server.list_resources()
        print(f"Found {len(resources)} resources:")
        for resource in resources:
            print(f"  - {resource.name}: {resource.uri}")
    except Exception as e:
        print(f"Error listing resources: {e}")
    
    # Test list tools
    print("\n2. Testing list_tools...")
    try:
        tools = await server.list_tools()
        print(f"Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"Error listing tools: {e}")
    
    # Test tool calls (only if credentials are available)
    if all([os.getenv('ATLASSIAN_BASE_URL'), 
            os.getenv('ATLASSIAN_USERNAME'), 
            os.getenv('ATLASSIAN_API_TOKEN')]):
        
        print("\n3. Testing tool calls...")
        
        # Test Jira search
        try:
            result = await server.call_tool("search_jira", {"jql": "project is not empty"})
            print(f"Jira search result: {len(result)} items")
        except Exception as e:
            print(f"Error testing Jira search: {e}")
        
        # Test Confluence search
        try:
            result = await server.call_tool("search_confluence", {"query": "test"})
            print(f"Confluence search result: {len(result)} items")
        except Exception as e:
            print(f"Error testing Confluence search: {e}")
        
        # Test Bitbucket search
        try:
            result = await server.call_tool("search_bitbucket", {"query": "test"})
            print(f"Bitbucket search result: {len(result)} items")
        except Exception as e:
            print(f"Error testing Bitbucket search: {e}")
    else:
        print("\n3. Skipping tool tests - missing Atlassian credentials")
        print("Set ATLASSIAN_BASE_URL, ATLASSIAN_USERNAME, and ATLASSIAN_API_TOKEN to test API calls")
    
    print("\nMCP Server test completed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())