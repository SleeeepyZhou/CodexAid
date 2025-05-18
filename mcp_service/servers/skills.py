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


@mcp.tool(description='检测到用户说出‘学习的时候’时，创建或更新一个表示学习中的计时任务', name='start_timer_on_study')
async def create_learning_task():
    import requests
    import json
    url = "https://deeppath.cc/api/mcp/standard"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba"
    }
    payload = {
        "functionCall": {
            "name": "createTask",
            "parameters": {
                "title": "学习任务",
                "description": "在指定时间内进行学习"
            }
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()
        task_id = result.get('taskId')
        task_status = result.get('status')
        return {
            "taskId": task_id,
            "status": task_status
        }
    else:
        return {
            "taskId": None,
            "status": None
        }

if __name__ == '__main__':
    mcp.run(transport='stdio')