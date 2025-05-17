import os, sys
currunt_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(currunt_dir, ".."))
from agent.baseagent import BaseAgent
from agent.prompt import DESIGNER

def load_deeppath():
    doc_path = os.path.join(currunt_dir, "..", "data", "books", "curl-commands.md")
    with open(doc_path) as f:
        doc = f.read()
        return doc

class Designer(BaseAgent):
    def __init__(
            self, 
            task: str,
            model = "Qwen/Qwen3-8B", 
            timeout = 30
            ):
        super().__init__(model, timeout)
        self.task = task
    
    def mcp_design(self):
        prompt = DESIGNER.format(user_prompt=self.task,info=load_deeppath())
        response = self.oneshot(prompt)
        print(response)
        data = self.find_json(response)
        return data["tools"]
    
if __name__ == '__main__':
    d = Designer("需要一个开灯，同时设置番茄钟计时的MCP工具")
    print(d.mcp_design())