import os
import json
from mcp_client import MCPClient

current_dir = os.path.dirname(os.path.abspath(__file__))
def load_serverlist():
    config_path = os.path.join(os.path.dirname(current_dir), "config/server_list.json")
    with open(config_path, 'r') as file:
        return json.load(file)

class MCPManager:
    def __init__(self):
        self.client_list: list[MCPClient] = []
        self.tool_client: dict[str, MCPClient] = {}
        self.tool_list: list = []
        self.is_ready: bool = False
    
    async def ready(self):
        self.is_ready = False
        server_list = load_serverlist()
        server_list = [os.path.join(os.path.dirname(current_dir), "server", server) for server in server_list]
        ready_server = []
        for server in server_list:
            client = MCPClient(server=server)
            try:
                name = await client.connect_to_server()
                tools = await client.get_tools()
                self.client_list.append(client)
                self.tool_list += tools
                for tool in tools:
                    self.tool_client[tool["name"]] = client
                ready_server.append(name)
                print(f"Server {name} ready.")
            except Exception as e:
                print(f"An error occurred while create client: {e}. For server {server}.")
                await client.cleanup()
                continue
        if ready_server:
            self.is_ready = True
        return ready_server
    
    def get_tools(self):
        return self.tool_list
    def get_toolnames(self):
        return self.tool_client.keys()
    def get_status(self):
        return self.is_ready

    async def call_tool(self, tool_name: str = None, tool_args: dict = None) -> list:
        if tool_name == None: 
            self.tool_list.clear()
            self.tool_client.clear()
            for client in self.client_list:
                tools = await client.get_tools()
                self.tool_list += tools
                for tool in tools:
                    self.tool_client[tool["name"]] = client
            return self.tool_list
        else:
            if not self.tool_client.get(tool_name):
                raise KeyError(f"Tool '{tool_name}' not found in tool list.")
            try:
                result = await self.tool_client[tool_name].call_tool(tool_name, tool_args)
                return result
            except Exception as e:
                raise RuntimeError(e)
    
    async def close(self):
        for client in self.client_list:
            await client.cleanup()
