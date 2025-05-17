import os, sys
currunt_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(currunt_dir, ".."))
from agent.designer import Designer
from agent.developer import Developer
from utils.mcpbuilder import build_mcp_server
from utils.mcpbuilder import ToolInf

import asyncio
from typing import List

async def mcp_create_async(task: str) -> str:
    designe = Designer(task)
    todo: List[dict] = designe.mcp_design()
    async def _run_dev(tool: dict) -> str | None:
        dev = Developer(
            tool["dev_tasks"],
            ToolInf(
                tool_name=tool["name"],
                description=tool["description"],
                codes=""
            )
        )
        success = await dev.dev()
        return dev.get_tool() if success else None

    results = await asyncio.gather(*[_run_dev(tool) for tool in todo])
    codes = [code for code in results if code is not None]
    return build_mcp_server(codes)

def mcp_create(task: str) -> str:
    """
    同步接口，向下兼容原有调用方式。
    """
    return asyncio.run(mcp_create_async(task))

if __name__ == '__main__':
    mcp_str = mcp_create("每次用户说学习的时候就开始DeepPath中的计时")
    temp_path = os.path.join(currunt_dir, "temp.py")
    with open(temp_path, "w") as t:
        t.write(mcp_str)