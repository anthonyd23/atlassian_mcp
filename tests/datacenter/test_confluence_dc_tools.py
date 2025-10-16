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
    spaces = result.get('results', [])
    space_key = spaces[0]['key'] if spaces else None
    print(f"Spaces: {result}")
    
    if space_key:
        print("\n2. Testing create_page...")
        result = await confluence.create_page(space_key, "DC Test Page", "<p>Testing DC tools</p>")
        page_id = result.get('id') if 'id' in result else None
        print(f"Create page: {result}")
        
        if page_id:
            print("\n3. Testing get_child_pages...")
            result = await confluence.get_child_pages(page_id)
            print(f"Child pages: {result}")
            
            print("\n4. Testing get_descendants...")
            result = await confluence.get_descendants(page_id)
            print(f"Descendants: {result}")
            
            print("\n5. Testing get_ancestors...")
            result = await confluence.get_ancestors(page_id)
            print(f"Ancestors: {result}")
            
            print("\n6. Testing cql_search...")
            result = await confluence.cql_search(f"type=page AND space={space_key}")
            print(f"CQL search: {result}")
            
            if len(spaces) > 1:
                print("\n7. Testing move_page...")
                target_space = spaces[1]['key']
                result = await confluence.move_page(page_id, target_space)
                print(f"Move page: {result}")
            
            print("\n8. Testing delete_page...")
            result = await confluence.delete_page(page_id)
            print(f"Delete page: {result}")
    
    print("\nConfluence Data Center tools test completed!")

if __name__ == "__main__":
    asyncio.run(test_confluence_dc_tools())
