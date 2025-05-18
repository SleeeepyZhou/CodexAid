import json
import os, sys
currunt_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(currunt_dir, ".."))
from utils.llm import LLMModel

class BaseAgent:
    def __init__(
            self,
            # model: str = "Qwen/Qwen3-8B", 
            model: str = "deepseek/deepseek-v3", 
            timeout: int = 30
            ):
        self.model = LLMModel(model, timeout)
        self.history = []

    @staticmethod
    def find_json(response : str):
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        json_str = response[json_start:json_end]
        data = json.loads(json_str)
        return data


    def oneshot(self, prompt: str):
        return self.model.chat(prompt).get("answer")

    def chat(self, prompt: str):
        massage = self.history + [{"role": "user", "content": prompt}]
        response = self.model.dialogue(massage).get("answer")
        if response:
            self.history += [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": response}
                ]
            return response
    
    def clear_history(self):
        self.history.clear()