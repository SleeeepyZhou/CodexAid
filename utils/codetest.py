import sys as real_sys

import time
import types
import builtins
import traceback
import asyncio
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

# default = '''from llm import LLMModel
# llm = LLMModel()
# def llm_call(prompt: str):
#     return llm.chat(prompt)'''
default = ""

def restricted_open(*args, **kwargs):
    mode = kwargs.get('mode', args[1] if len(args) > 1 else 'r')
    if any(flag in mode for flag in ('w', 'a', '+')):
        raise IOError("File write operations are disabled")
    return builtins.open(*args, **kwargs)

class CodeResponse(BaseModel):
    output: str
    error: str
    execution_time: float

class CodeTester:
    _global_pool = ThreadPoolExecutor(max_workers=100)
    _semaphore = asyncio.Semaphore(100)

    def __init__(self, code: str, timeout: int = 180, allowed_paths: list[str] | None = None):
        self.code = default + "\n" + code
        self.timeout = timeout
        self.allowed_paths = allowed_paths

    def _task(self) -> CodeResponse:
        cap_out = StringIO()
        cap_err = StringIO()

        # 构造隔离模块
        module = types.ModuleType("dynamic_module")
        env = module.__dict__

        # 注入沙箱环境
        env['__builtins__'] = builtins
        env['print'] = print  # use default, under redirect it writes to cap_out
        env['open'] = restricted_open

        fake_sys = types.SimpleNamespace(
            modules=real_sys.modules,
            platform=real_sys.platform,
            version=real_sys.version,
            stdin=StringIO(),
            stdout=cap_out,
            stderr=cap_err
        )
        fake_sys.path = list(self.allowed_paths) if self.allowed_paths is not None else list(real_sys.path)
        env['sys'] = fake_sys

        start = time.time()
        # 使用 contextlib 重定向 stdout/stderr，安全不影响全局
        with redirect_stdout(cap_out), redirect_stderr(cap_err):
            try:
                exec(self.code, env)
            except Exception:
                traceback.print_exc(file=cap_err)
        duration = time.time() - start

        return CodeResponse(
            output=cap_out.getvalue(),
            error=cap_err.getvalue(),
            execution_time=duration
        )

    async def run(self) -> CodeResponse:
        async with CodeTester._semaphore:
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(CodeTester._global_pool, self._task)
            try:
                result = await asyncio.wait_for(future, self.timeout)
            except asyncio.TimeoutError:
                msg = f"Execution timed out after {self.timeout}s"
                return CodeResponse(output='', error=msg, execution_time=self.timeout)
        return result

# test
async def main():
    complex_code = '''
print("开始测试：")
if __name__ == '__main__':
    print("ismain")
'''
    executor = CodeTester(complex_code, timeout=5)
    response = await executor.run()
    print('=== OUTPUT ===')
    print(response.output)
    print('=== ERROR ===')
    print(response.error)
    print('=== TIME ===')
    print(f"{response.execution_time:.3f}s")


async def batch_test():
    codes = [
        'print("Task 1 start"); import time; time.sleep(0.1); print("Task 1 end")',
        'print("Task 2 start"); x = 5/0', 
        'print("Task 3 start"); from math import sqrt; print(sqrt(16))',
        'print("Task 4 start"); import sys; sys.stdout.write("Sys write in Task 4")',
        'print("Task 5 start"); print(llm.chat("测试一下"))'
    ]
    executors = [CodeTester(code, timeout=30) for code in codes]
    results = await asyncio.gather(*(exe.run() for exe in executors))
    for idx, res in enumerate(results, 1):
        print(f"--- Result of task {idx} ---")
        print("Output:")
        print(res.output)
        print("Error:")
        print(res.error)
        print(f"Time: {res.execution_time:.3f}s")

if __name__ == '__main__':
    asyncio.run(main())