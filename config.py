EMBEDDING = {
    "url": "https://api.siliconflow.cn/v1/embeddings",
    "key": "sk-zkhkjdforqphtbiqpitshibzjjifwfbthncnpxsqsmxvmfgj"
}

LLM = {
    "url": "https://api.siliconflow.cn/v1/chat/completions",
    "key": "sk-zkhkjdforqphtbiqpitshibzjjifwfbthncnpxsqsmxvmfgj"
}

# LLM = {
#     "url": "https://api.qnaigc.com/v1/chat/completions",
#     "key": "sk-b3713ef5fb3871bb7b4ba211af14620ace8e263365a008966313a9af9b9d2ee6"
# }

import os
currunt_dir = os.path.dirname(__file__)
MCPPATH = os.path.join(currunt_dir, "mcp_service", "servers", "skills.py")

TOOLPORT = 8848