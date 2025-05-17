import os, sys
currunt_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(currunt_dir, "..", ".."))

from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Skills")

@mcp.tool() # MCP tool identification
async def example_func(example_arg: str) -> str:
    """Please provide a description of the function here.

    Args:
        example_arg: Describe the input here.
    """
    # Here is the specific function of the function.
    print(example_arg)
    return example_arg # Return a string.

@mcp.tool(description="通过用户指令，创建新的MCP", name="new_mcp")
async def new_mcp(prompt: str):
    import requests
    import json
    try:
        resp = requests.post(
            f"http://127.0.0.1:8848/new_mcp",
            json=json.dumps({"prompt":prompt})
        )
        result = resp.json()
        if result["status"] == "ok":
            return result["status"]
        else:
            return f"Error: {result["status"]}"
    except Exception as e:
        return f"Request failed: {e}"

if __name__ == '__main__':
    mcp.run(transport='stdio')