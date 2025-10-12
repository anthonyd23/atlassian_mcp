import json
import asyncio
from mcp_server.main import server
from mcp.server.stdio import stdio_server
import io
import sys

def lambda_handler(event, context):
    """AWS Lambda handler for MCP server"""
    
    # Extract the MCP request from the event
    mcp_request = event.get('body', '')
    if isinstance(mcp_request, str):
        mcp_request = json.loads(mcp_request)
    
    # Create in-memory streams
    input_stream = io.StringIO(json.dumps(mcp_request))
    output_stream = io.StringIO()
    
    async def run_mcp():
        # Mock stdio streams with our in-memory streams
        class MockStream:
            def __init__(self, stream):
                self.stream = stream
            
            async def read(self, n=-1):
                return self.stream.read(n).encode()
            
            async def write(self, data):
                if isinstance(data, bytes):
                    data = data.decode()
                self.stream.write(data)
                return len(data)
        
        read_stream = MockStream(input_stream)
        write_stream = MockStream(output_stream)
        
        try:
            await server.run(read_stream, write_stream, server.create_initialization_options())
        except Exception as e:
            return {'error': str(e)}
    
    # Run the async MCP server
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(run_mcp())
        response_data = output_stream.getvalue()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': response_data or json.dumps({'status': 'success'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
    finally:
        loop.close()