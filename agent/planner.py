import os, sys
currunt_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(currunt_dir, ".."))
from agent.base import BaseAgent
from agent.templates import PLANNER

class Planner(BaseAgent):
    def __init__(
            self,
            model = "Qwen/Qwen3-8B",
            timeout = 30
    ):
        super().__init__(model, timeout)

    def plan(self, task: str):
        prompt = PLANNER.format(task=task)
        response = self.oneshot(prompt, format=True)
        data = self.find_json(response)