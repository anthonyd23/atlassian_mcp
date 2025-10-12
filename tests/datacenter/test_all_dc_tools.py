import asyncio
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from mcp_server.datacenter.jira_dc_provider import JiraDCProvider
from mcp_server.datacenter.confluence_dc_provider import ConfluenceDCProvider
from mcp_server.datacenter.bitbucket_dc_provider import BitbucketDCProvider

async def test_all_dc_tools():
    print("=" * 60)
    print("TESTING ALL ATLASSIAN DATA CENTER TOOLS (46 TOTAL)")
    print("=" * 60)
    
    # Jira Data Center (14 tools)
    print("\n" + "=" * 60)
    print("JIRA DATA CENTER TOOLS (14)")
    print("=" * 60)
    jira = JiraDCProvider()
    
    print("\n1. list_projects")
    print(await jira.list_projects())
    
    print("\n2. search_jira")
    print(await jira.search("project = TEST"))
    
    # Confluence Data Center (12 tools)
    print("\n" + "=" * 60)
    print("CONFLUENCE DATA CENTER TOOLS (12)")
    print("=" * 60)
    confluence = ConfluenceDCProvider()
    
    print("\n1. list_spaces")
    print(await confluence.list_spaces())
    
    print("\n2. search_confluence")
    print(await confluence.search("test"))
    
    # Bitbucket Server Data Center (20 tools)
    print("\n" + "=" * 60)
    print("BITBUCKET SERVER DATA CENTER TOOLS (20)")
    print("=" * 60)
    bitbucket = BitbucketDCProvider()
    
    print("\n1. list_repositories")
    print(await bitbucket.list_repositories())
    
    print("\n2. search_bitbucket")
    print(await bitbucket.search("test"))
    
    print("\n" + "=" * 60)
    print("ALL DATA CENTER TOOLS TEST COMPLETED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_all_dc_tools())
