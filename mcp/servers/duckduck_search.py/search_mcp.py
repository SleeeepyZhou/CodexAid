from mcp.server.fastmcp import FastMCP

mcp = FastMCP("searcher")

web_search_doc = """
Use search engine to search information from the web for the given query.

    Args:
        query (str): The search query to submit to the search engine. 
        max_results (int): The maximum number of webpage results to return. (default: :obj:`5`)
        web (str): The website to limit the search to. (default: :obj:`""`)
        parse (bool): Whether to parse the web content. (default: :obj:`True`)

    Returns:
        list: A list of dictionaries, each with:
            - 'result_id' (int): The id of the result.
            - 'title' (str): The title of the webpage.
            - 'url' (str): The URL of the webpage.
            - 'description' (str): The description of the webpage.
            - 'content' (str): The detailed content of the webpage.
            - 'score' (float): The score of the webpage.
"""

import os, sys
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, '../..'))

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

_executor = ThreadPoolExecutor(max_workers=32)

from tools.websearch.retriever import (
        google_search as sync_google_search,
        search_camel as sync_search_camel
    )
from tools.websearch.web_parse import web_searcher as sync_web_searcher

@mcp.tool(description=web_search_doc, name="web_search")
async def web_search(
    query: str,
    max_results: int = 5,
    parse: bool = True,
    web: str = "",
    timeout: Optional[float] = 10.0
) -> list:
    loop = asyncio.get_running_loop()
    if parse:
        try:
            raw_results = await asyncio.wait_for(
                loop.run_in_executor(
                    _executor,
                    lambda: sync_web_searcher(query, max_results, web)
                ),
                timeout=10
            )
        except asyncio.TimeoutError:
            return []
        return [{
                "title": item["title"],
                "url": item["url"],
                **{k: v for k, v in item.items() if k not in ["description", "title", "url"]}
            } for item in raw_results]
    else:
        try:
            results = await asyncio.wait_for(
                loop.run_in_executor(
                    _executor,
                    lambda: sync_search_camel(query, tool_name="search_google")
                ),
                timeout=timeout
            )
        except Exception as e:
            print(f"search_camel 失败 ({e}), 回退到 google_search")
            results = await loop.run_in_executor(
                _executor,
                lambda: sync_google_search(query)
            )
        return [{
            "title": result["title"],
            "url": result["url"],
            "content": result.get("description", ""),
            "score": None
        } for result in results]

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')