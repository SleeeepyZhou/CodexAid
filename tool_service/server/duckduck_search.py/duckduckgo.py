import sys,os
current_dir = os.path.dirname(__file__)

from duckduckgo_search import DDGS


USE_PROXY = None

def duckduckgo(
    query: str, 
    web: str = "zhihu.com", 
    max_results: int = 10,
    timelimit: str = None,  # 时间范围 d, w, m, y
    region: str = "wt-wt"
) -> tuple[list, dict]:
    """
    DuckDuckGo 搜索
    :param query: 搜索关键词
    :param web: 网站过滤
    :param max_results: 返回结果数量
    :param region: 地区代码 (cn-zh 大陆, wt-wt 全球)
    :param timelimit: 时间过滤 (d: 天, w: 周, m: 月, y: 年)
    :return: 搜索结果
    (
    [url1,url2],
    {
        0:{
            "title": 标题,
            "description": 摘要
        },
        1:{
            "title": 标题,
            "description": 摘要
        }
    }
    )
    """
    if web != "":
        query += f" site:{web}"
    try:
        with DDGS(proxy= USE_PROXY, timeout= 3) as ddgs:
            results = {}
            link_list = []
            kwargs = {
                "keywords": query,
                "region": region,
                "timelimit": timelimit,
                "max_results": max(8, max_results+5)
            }

            for idx, result in enumerate(ddgs.text(**kwargs)):
                url = result.get("href", "")
                if web.lower() in url:
                    link_list.append(url)
                    results[idx] = {
                        "title": result.get("title", "无标题"),
                        "description": result.get("body", "无摘要"),
                    }
                if len(link_list) >= max_results:
                    break
            return (link_list,results)
    
    except Exception as e:
        print(f"搜索出错: {str(e)}")
        return ([],{})