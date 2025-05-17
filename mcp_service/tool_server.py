import json
import uvicorn
from typing import Dict
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from manager import MCPManager
manager = MCPManager()

import os, sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))
from config import TOOLPORT
from scr.work import mcp_create

def load_agent_tools():
    config_path = os.path.join(current_dir, "agent_tools.json")
    with open(config_path, 'r') as file:
        return json.load(file)
agent_tools = load_agent_tools()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await manager.ready()
    yield
    for client in manager.client_list:
        await client.cleanup()
app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health_check():
    status = "ok" if manager.get_status() else "unready"
    return {"status": status}

@app.get("/reset")
async def reset():
    error = ""
    try:
        global agent_tools
        agent_tools = load_agent_tools()
        await manager.ready()
        status = "Reset ok. " + error if error else ("ok" if manager.get_status() else "unready")
        return {"status": status}
    except Exception as e:
        print(f"Error during reset: {e}")
        return {"status": e}

@app.get("/get_tool")
async def get_tools():
    return manager.get_tools()

@app.get("/get_tool/{agent_name}")
async def get_tools(agent_name: str):
    if (not agent_tools.get(agent_name)) or (not agent_tools[agent_name]):
        return manager.get_tools()
    return agent_tools[agent_name]

# Call
@app.post("/call_tool/{tool_name}")
async def create_tool_task(tool_name: str, tool_args: Dict):
    tool_names = manager.get_toolnames()
    if tool_name not in tool_names:
        raise HTTPException(404, "Tool not found")
    result = None
    status = False
    try:
        result = await manager.call_tool(
            tool_name,
            tool_args
        )
        status = True
    except Exception as e:
        result = f"Error: {str(e)}"
        status = False
    finally:
        return {"status": status, "result": result}

SKILLS = os.path.join(current_dir, "servers", "skills.py")
@app.post("/new_mcp")
async def new_mcp(prompt: str):
    server = mcp_create(prompt)
    with open(SKILLS, "w") as skill:
        skill.write(server)
    return await reset()

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=TOOLPORT,
        lifespan="on"
        # reload=True
    )