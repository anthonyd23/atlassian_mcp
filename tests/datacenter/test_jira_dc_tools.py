import asyncio
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from mcp_server.datacenter.jira_dc_provider import JiraDCProvider

async def test_jira_dc_tools():
    print("Testing Jira Data Center Tools...")
    jira = JiraDCProvider()
    
    print("\n1. Testing list_projects...")
    result = await jira.list_projects()
    print(f"Projects: {result}")
    
    print("\n2. Testing search_jira...")
    result = await jira.search("project = TEST")
    print(f"Search results: {result}")
    
    print("\n3. Testing get_issue...")
    result = await jira.get_issue("TEST-1")
    print(f"Issue: {result}")
    
    print("\nJira Data Center tools test completed!")

if __name__ == "__main__":
    asyncio.run(test_jira_dc_tools())
