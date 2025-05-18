EMBEDDING = {
    "url": "https://api.siliconflow.cn/v1/embeddings",
    "key": "***REMOVED***"
}

LLM = {
    "url": "https://api.siliconflow.cn/v1/chat/completions",
    "key": "***REMOVED***"
}

# LLM = {
#     "url": "https://api.qnaigc.com/v1/chat/completions",
#     "key": "***REMOVED***"
# }

import os
currunt_dir = os.path.dirname(__file__)
MCPPATH = os.path.join(currunt_dir, "mcp_service", "servers", "skills.py")

TOOLPORT = 8848