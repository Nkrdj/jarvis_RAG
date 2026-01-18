import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    # Get absolute path to the server script
    script_path = os.path.abspath("rag_mcp.py")
    
    print(f"Connecting to MCP server at: {script_path}...")
    
    # Configure the server execution parameters
    server_params = StdioServerParameters(
        command=sys.executable, # Use the current python interpreter
        args=[script_path],
        env=os.environ.copy()
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 1. Initialize the connection
                await session.initialize()
                print("\n[Connected] Server initialized successfully.")
                
                # 2. List available tools
                tools_response = await session.list_tools()
                print(f"\n[Tools Found]: {len(tools_response.tools)}")
                for tool in tools_response.tools:
                    print(f"- {tool.name}: {tool.description}")
                
                # 3. Test a query
                query = "What is RAG?"
                print(f"\n[Testing Tool] query_rag('{query}')...")
                
                # Call the tool
                result = await session.call_tool("query_rag", arguments={"query": query})
                
                # Print result
                if result.content:
                    print("\n[Result]:")
                    print(result.content[0].text)
                else:
                    print("No content returned.")
                    
    except Exception as e:
        print(f"\n[Error] Connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Windows-specific event loop policy to avoid issues with subprocesses
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    asyncio.run(run())
