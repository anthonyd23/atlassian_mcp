import asyncio
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from mcp_server.datacenter.bitbucket_dc_provider import BitbucketDCProvider

async def test_bitbucket_dc_tools():
    print("Testing Bitbucket Server Data Center Tools...")
    bitbucket = BitbucketDCProvider()
    
    print("\n1. Testing list_repositories...")
    result = await bitbucket.list_repositories()
    print(f"Repositories: {result}")
    
    print("\n2. Testing search...")
    result = await bitbucket.search("test")
    print(f"Search results: {result}")
    
    print("\nBitbucket Server Data Center tools test completed!")

if __name__ == "__main__":
    asyncio.run(test_bitbucket_dc_tools())
