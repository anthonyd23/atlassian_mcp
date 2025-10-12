#!/usr/bin/env python3
"""Test all 50 MCP tools"""
import asyncio
import os
import sys

async def run_tests():
    print("=" * 60)
    print("Testing All 50 Atlassian MCP Tools")
    print("=" * 60)
    print()
    
    # Check credentials
    if not all([os.getenv('ATLASSIAN_BASE_URL'), 
                os.getenv('ATLASSIAN_USERNAME'), 
                os.getenv('ATLASSIAN_API_TOKEN')]):
        print("ERROR: Missing Atlassian credentials")
        print("Set: ATLASSIAN_BASE_URL, ATLASSIAN_USERNAME, ATLASSIAN_API_TOKEN")
        return
    
    if not os.getenv('BITBUCKET_API_TOKEN'):
        print("WARNING: BITBUCKET_API_TOKEN not set - Bitbucket tests may fail")
        print()
    
    # Test Jira (14 tools)
    print("\n" + "=" * 60)
    print("JIRA TOOLS (14 tools)")
    print("=" * 60)
    from test_jira_tools import test_jira_tools
    try:
        await test_jira_tools()
    except Exception as e:
        print(f"Jira tests failed: {e}")
    
    # Test Confluence (12 tools)
    print("\n" + "=" * 60)
    print("CONFLUENCE TOOLS (12 tools)")
    print("=" * 60)
    from test_confluence_tools import test_confluence_tools
    try:
        await test_confluence_tools()
    except Exception as e:
        print(f"Confluence tests failed: {e}")
    
    # Test Bitbucket (24 tools)
    print("\n" + "=" * 60)
    print("BITBUCKET TOOLS (24 tools)")
    print("=" * 60)
    from test_bitbucket_tools import test_bitbucket_tools
    try:
        await test_bitbucket_tools()
    except Exception as e:
        print(f"Bitbucket tests failed: {e}")
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("Total: 50 tools (14 Jira + 12 Confluence + 24 Bitbucket)")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_tests())
