import json
import os
import uuid
import asyncio
import uvicorn
from typing import Dict
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from manager import MCPManager

manager = MCPManager()

current_dir = os.path.dirname(os.path.abspath(__file__))
temp_dir = os.path.join(current_dir, "temp")
os.makedirs(temp_dir, exist_ok=True)

def load_agent_tools():
    config_path = os.path.join(current_dir, "config", "agent_tools.json")
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

def write_lib():
    if not manager.get_status():
        with open(os.path.join(temp_dir, "tools.py"), "w") as py_lib:
            py_lib.write("")
    
    initial = "from ..tool_caller import call_tool\n"
    code = ""
    for tool in manager.get_tools():
        schema = tool.get("input_schema")
        arg = ""
        arg_dict = "    tool_args = {"
        if schema:
            for in_arg in schema.get("properties").keys():
                default = ""
                if not schema.get("required").has(in_arg):
                    default = "=None"
                arg += f"{in_arg}{default},"
                arg_dict += f"'{in_arg}':{in_arg},"
        arg_dict += "}"

        code += f"def {tool['name']}({arg}):\n{arg_dict}\n    result = call_tool('{tool['name']}', tool_args)\n    return result\n"
    with open(os.path.join(temp_dir, "tools.py"), "w") as py_lib:
        py_lib.write(initial + code)

@app.get("/health")
async def health_check():
    status = "ok" if manager.get_status() else "unready"
    return {"status": status}

@app.get("/reset")
async def reset():
    try:
        global agent_tools
        agent_tools = load_agent_tools()
        await manager.ready()
        status = "ok" if manager.get_status() else "unready"
        write_lib()
        return {"status": status}
    except Exception as e:
        print(f"Error during reset: {e}")
        return {"status": "error"}

@app.get("/get_tool")
async def get_tools():
    return manager.get_tools()

@app.get("/get_tool/{agent_name}")
async def get_tools(agent_name: str):
    if (not agent_tools.get(agent_name)) or (not agent_tools[agent_name]):
        return manager.get_tools()
    return agent_tools[agent_name]


# Call
tasks: Dict[str, dict] = {}

@app.post("/call")
async def create_task(code: str):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "tool": "run_code",
        "arg": code,
        "status": "pendding",
        "result": None,
        "error": None,
    }
    asyncio.create_task(execute_code(task_id, code))
    return {"task_id": task_id}
async def execute_code(task_id: str, code: str):
    update_task(task_id, {"status": "running"})

    file_path = os.path.join(temp_dir, f"{task_id}.py")
    with open(file_path, "w") as f:
        f.write(code)
    
    try:
        proc = await asyncio.create_subprocess_exec(
            "python",
            file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        if proc.returncode == 0:
            update_task(task_id, {
                "status": "completed",
                "result": stdout.decode().strip(),
                "error": None
            })
        else:
            raise RuntimeError(stderr.decode().strip())
        
    except Exception as e:
        update_task(task_id, {
            "status": "failed",
            "result": None,
            "error": f"{type(e).__name__}: {str(e)}"
        })
    finally:
        try:
            os.remove(file_path)
        finally:
            await asyncio.sleep(300)
            tasks.pop(task_id, None)

@app.post("/call_tool/{tool_name}")
async def create_tool_task(tool_name: str, tool_args: Dict):
    tool_names = manager.get_toolnames()
    if tool_name not in tool_names:
        raise HTTPException(404, "Tool not found")
    task_id = str(uuid.uuid4())
    
    tasks[task_id] = {
        "tool": tool_name,
        "arg": tool_args,
        "status": "pendding",
        "result": None,
        "error": None,
    }

    asyncio.create_task(execute_tool(task_id, tool_name, tool_args))
    
    return {"task_id": task_id}
async def execute_tool(task_id: str, tool_name: str, tool_args: Dict):
    update_task(task_id, {"status": "running"})
    try:
        result = await manager.call_tool(
            tool_name,
            tool_args
        )
        
        update_task(task_id, {
            "status": "completed",
            "result": result
        })
        
    except Exception as e:
        update_task(task_id, {
            "status": "failed",
            "error": str(e)
        })
    finally:
        await asyncio.sleep(300)
        tasks.pop(task_id, None)

def update_task(task_id: str, updates: dict):
    if task_id in tasks:
        tasks[task_id].update(updates)

@app.get("/callback/{task_id}")
async def task_updates(task_id: str):
    while True:
        task = tasks.get(task_id)
        if not task:
            return {
                "event": "error", 
                "data": "The task does not exist or has been cleared."
            }
        if task["status"] in ("completed", "failed", "cancelled"):
            return {
                    "status": task["status"],
                    "result": task["result"],
                    "error": task["error"]
                }
        await asyncio.sleep(1)


@app.get("/cancel/{task_id}")
async def cancel_task(task_id: str):
    if task := tasks.get(task_id):
        task["status"] = "cancelled"
        return {
                "data": {
                    "status": task["status"],
                    "result": task["result"],
                    "error": task["error"]
                }
            }
    else:
        return {
                "event": "error", 
                "data": "The task does not exist or has been cleared."
            }

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8848,
        lifespan="on"
        # reload=True
    )