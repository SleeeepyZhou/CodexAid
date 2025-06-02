import re
from typing import List
from pydantic import BaseModel
import os, sys
currunt_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(currunt_dir, ".."))
from config import MCPPATH

TOOL_TEMPLATE = '''@mcp.tool(description={description!r}, name={tool_name!r})\nasync def '''

ENDSTR = '''if __name__ == '__main__':
    mcp.run(transport='stdio')'''

class ToolInf(BaseModel):
    tool_name: str
    description: str
    codes: str

def build_tool_block(tool: ToolInf) -> str:
    """
    Given tool metadata, return the formatted code block for that tool.

    Replaces the first function definition (def or async def) with
    @mcp.tool(...)\nasync def ...
    """
    codes = tool.codes.lstrip()
    head = TOOL_TEMPLATE.format(
        description=tool.description,
        tool_name=tool.tool_name
    )
    # 正则替换中间出现的 def 或 async def
    codes = re.sub(r'^(?:async\s+)?def\s+', head, codes, count=1, flags=re.MULTILINE)
    return codes

def build_mcp_server(
    tools: List[ToolInf]
) -> None:
    """
    Assemble and write the MCP server file with given tools.

    Args:
        tools: List of dicts with keys 'tool_name', 'description', 'codes'.
        mcp_name: Name identifier for FastMCP (as passed in constructor).
        output_path: File path to save the generated server script.
    """
    tool_blocks = [build_tool_block(t) for t in tools]
    all_tools_code = "\n".join(tool_blocks)

    with open(MCPPATH) as f:
        mcp_str = f.read()

    server_code = mcp_str.replace(ENDSTR, all_tools_code + "\n\n" + ENDSTR)

    return server_code

if __name__ == '__main__':
    example_tools = [
        ToolInf(
            tool_name='example_func',
            description='Please provide a description of the function here.',
            codes='''def example_func(example_arg: str) -> str:
    print(example_arg)
    return example_arg'''
        )
    ]
    print(build_mcp_server(tools=example_tools))
