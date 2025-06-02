from dotenv import load_dotenv
import os

load_dotenv()

EMBEDDING = {
    "url": os.getenv("EMBEDDING_API_URL", "https://api.siliconflow.cn/v1/embeddings"),
    "key": os.getenv("EMBEDDING_API_KEY")
}

LLM = {
    "url": os.getenv("LLM_API_URL", "https://api.siliconflow.cn/v1/chat/completions"),
    "key": os.getenv("LLM_API_KEY")
}

currunt_dir = os.path.dirname(__file__)
MCPPATH = os.path.join(currunt_dir, "mcp", "servers", "skills.py")

TOOLPORT = 8848