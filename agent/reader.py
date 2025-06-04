import os, sys
currunt_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(currunt_dir, ".."))
from agent.base import BaseAgent
from utils import RAGDatabase

class Reader(BaseAgent):
    def __init__(
            self, 
            task: str,
            model = "Qwen/Qwen3-8B", 
            timeout = 30
            ):
        super().__init__(model, timeout)

        self.table = task
        self.database = RAGDatabase()
        
    pass