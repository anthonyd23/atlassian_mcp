import asyncio
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from mcp_server.datacenter.confluence_dc_provider import ConfluenceDCProvider

async def test_confluence_dc_tools():
    print("Testing Confluence Data Center Tools...")
    confluence = ConfluenceDCProvider()
    
    print("\n1. Testing list_spaces...")
    result = await confluence.list_spaces()
    print(f"Spaces: {result}")
    
    print("\n2. Testing search...")
    result = await confluence.search("test")
    print(f"Search results: {result}")
    
    print("\nConfluence Data Center tools test completed!")

if __name__ == "__main__":
    asyncio.run(test_confluence_dc_tools())
