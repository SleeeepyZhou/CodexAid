import os, sys
currunt_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(currunt_dir, ".."))
from utils.rag_sql import RAGDatabase
from agent.baseagent import BaseAgent

class Reader(BaseAgent):
    pass