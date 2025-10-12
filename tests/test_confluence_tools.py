#!/usr/bin/env python3
"""Test all 12 Confluence tools"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_server.confluence_provider import ConfluenceProvider

async def test_confluence_tools():
    print("Testing Confluence Tools...\n")
    confluence = ConfluenceProvider()
    
    # 1. List spaces
    print("1. list_spaces")
    result = await confluence.list_spaces()
    spaces = result.get('results', [])
    space_key = spaces[0]['key'] if spaces else None
    print(f"   Result: Found {len(spaces)} spaces\n")
    
    if space_key:
        # 2. Get space
        print("2. get_space")
        result = await confluence.get_space(space_key)
        print(f"   Result: {result}\n")
        
        # 3. List pages
        print("3. list_pages")
        result = await confluence.list_pages(space_key)
        print(f"   Result: {result}\n")
        
        # 4. Create page
        print("4. create_page")
        result = await confluence.create_page(space_key, "MCP Test Page", "<p>Testing MCP tools</p>")
        page_id = result.get('id') if 'id' in result else None
        print(f"   Result: {result}\n")
        
        if page_id:
            # 5. Get page
            print("5. get_page")
            result = await confluence.get_page(page_id)
            version = result.get('version', {}).get('number', 1)
            print(f"   Result: {result}\n")
            
            # 6. Get page by title
            print("6. get_page_by_title")
            result = await confluence.get_page_by_title(space_key, "MCP Test Page")
            print(f"   Result: {result}\n")
            
            # 7. Update page
            print("7. update_page")
            result = await confluence.update_page(page_id, "MCP Test Page Updated", "<p>Updated content</p>", version)
            print(f"   Result: {result}\n")
            
            # 8. Add page comment
            print("8. add_page_comment")
            result = await confluence.add_page_comment(page_id, "<p>Test comment</p>")
            print(f"   Result: {result}\n")
            
            # 9. Get page comments
            print("9. get_page_comments")
            result = await confluence.get_page_comments(page_id)
            print(f"   Result: {result}\n")
            
            # 10. Get page attachments
            print("10. get_page_attachments")
            result = await confluence.get_page_attachments(page_id)
            print(f"   Result: {result}\n")
            
            # 11. Search confluence
            print("11. search_confluence")
            result = await confluence.search("MCP Test")
            print(f"   Result: {result}\n")
            
            # 12. Delete page
            print("12. delete_page")
            result = await confluence.delete_page(page_id)
            print(f"   Result: {result}\n")
    else:
        print("No spaces found - skipping page tests\n")
    
    print("Confluence tools test completed!")

if __name__ == "__main__":
    asyncio.run(test_confluence_tools())
