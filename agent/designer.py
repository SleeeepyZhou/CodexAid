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
        response = self.oneshot(
            prompt,
            format=True
            )
        data = self.find_json(response)
        print(data)
        return data["tools"]
    
if __name__ == '__main__':
    d = Designer("每次用户输入学习的时候就开始打开台灯")
    print(d.mcp_design())