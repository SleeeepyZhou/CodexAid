import os, sys
currunt_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(currunt_dir, ".."))
from utils.codetest import CodeTester
from utils.mcpbuild import ToolInf
from agent.base import BaseAgent
from agent.templates import DEVELOPER, DEV_CON

def load_deeppath():
    doc_path = os.path.join(currunt_dir, "..", "data", "books", "curl-commands.md")
    with open(doc_path) as f:
        doc = f.read()
        return doc

class Developer(BaseAgent):
    def __init__(
            self, 
            task: str,
            tool: ToolInf,
            model = "Qwen/Qwen3-8B", 
            timeout = 30
            ):
        super().__init__(model, timeout)
        self.task = task
        self.tool = tool
        self.code = ""
        self.test = ""
        self.initial_dev()

    def initial_dev(self):
        prompt = DEVELOPER.format(task=self.task,info=load_deeppath())
        response = self.oneshot(
            prompt,
            format=True
            )
        data = self.find_json(response)
        print(data)
        self.code = data["codes"]
        self.test = data["test"]

    async def code_test(self):
        tester = CodeTester(self.code + "\n" + self.test)
        result = await tester.run()
        test = f"Output: {result.output}\nError: {result.error}"
        prompt = DEV_CON.format(task=self.task,info=load_deeppath(),code=self.code,result=test)
        response = self.oneshot(
            prompt,
            format=True
            )
        data = self.find_json(response)
        print(data)
        if not data["ready"]:
            self.code = data["codes"]
            self.test = data["test"]
        return data
    
    async def dev(self):
        test_ready = False
        test_times = 0
        while not test_ready and test_times < 5:
            result = await self.code_test()
            test_ready = result["ready"]
            test_times += 1
        return test_ready
    
    def get_tool(self):
        self.tool.codes = self.code
        return self.tool

if __name__ == "__main__":
    import asyncio
    dev = Developer(
        "创建一个自动化规则，当用户输入包含'学习'时触发，调用toggleLamp接口将台灯状态设置为on",
        ToolInf(
            tool_name="trigger_study_mode",
            description="检测到用户输入学习时，打开台灯",
            codes=""
        )
        )
    print(asyncio.run(dev.dev()))
    print(dev.get_tool().codes)