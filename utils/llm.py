import time
import json
import requests
import os, sys
import subprocess

current_dir = os.path.dirname(__file__)

class LLMModel:
    def __init__(
            self, 
            model_name: str = "Qwen3-30B-A3B-Q4_K_M",
            port: int = 9527, 
            timeout: int = 20
        ):
        self.model_name = model_name
        
        self.model_path = os.path.normpath(os.path.join(current_dir, "..", "models", f"{model_name}.gguf"))
        self.model_path = self.model_path.replace("\\", "/")
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model path does not exist: {self.model_path}")
        
        self.port = port
        self.base_url = f"http://localhost:{self.port}/v1"

        self._start_server()
        if not self._wait_for_server_ready(timeout):
            raise RuntimeError(f"Server did not start within {timeout} seconds")

    def _start_server(self):
        """启动后台服务进程"""
        server_path = os.path.normpath(
            os.path.join(current_dir, "..", "llama", "llama-server.exe")
        ).replace("\\", "/")
        
        cmd = [
            server_path,
            "-m", self.model_path,
            "-ngl", "999",
            "--flash-attn",
            # "--split-mode", "layer",
            # "--tensor-split", "0,1",
            # "--main-gpu", "1",
            "--no-mmap",
            "--port", str(self.port)
        ]

        self.proc = subprocess.Popen(
            cmd,
            cwd=os.path.dirname(server_path),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
    
    def _wait_for_server_ready(self, timeout: int = 20) -> bool:
        health_url = f"http://localhost:{self.port}/health"
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                resp = requests.get(health_url, timeout=1)
                if resp.status_code == 200:
                    return True
            except requests.RequestException:
                time.sleep(1)
        return False
    
    @staticmethod
    def _split_reasoning(response: str) -> dict:
        """
        Split the reasoning from the response.
        """
        if "<think>" not in response:
            return {
                "reasoning": "",
                "answer": response.strip()
            }
        
        temp = response.split("<think>\n")[1]
        temp = temp.split("\n</think>\n")
        return {
            "reasoning": temp[0].strip(),
            "answer": temp[1].strip()
        }

    def chat(self, prompt: str, role: str = "user", **params) -> dict:
        """
        Standard chat completion.
        messages: list of {"role": ..., "content": ...}
        params: other OpenAI parameters (e.g., max_tokens)
        """
        messages = [{"role": role, "content": prompt}]
        params.pop('stream', None)
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            **params
        }
        url = f"{self.base_url}/chat/completions"
        resp = requests.post(url, json=payload, timeout=params.get("timeout", 30))
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return self._split_reasoning(content)

    def stream_chat(self, prompt: str, role: str = "user", **params):
        """
        Streaming chat completion.
        yields each chunk of data as it arrives.
        """
        messages = [{"role": role, "content": prompt}]
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
            **params
        }
        url = f"{self.base_url}/chat/completions"

        reasoning_buf = []
        answer_buf = []
        in_answer = False
        with requests.post(url, json=payload, stream=True, timeout=params.get("timeout", 30)) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines(decode_unicode=False):
                if not line:
                    continue
                if line.startswith(b'data: '):
                    data = line[len(b'data: '):]
                else:
                    data = line
                if data.strip() == b"[DONE]":
                    break
                try:
                    data = data.decode('utf-8').strip()
                    chunk = json.loads(data)
                    delta = chunk["choices"][0].get("delta", {}).get("content", "")
                except Exception:
                    delta = data

                if not in_answer:
                    reasoning_buf.append(delta)
                    combined = ''.join(reasoning_buf)
                    if '</think>' in combined:
                        in_answer = True
                        # split out answer start
                        post = combined.split('</think>', 1)[1]
                        if post:
                            answer_buf.append(post)
                    yield {
                        "reasoning": combined.split('</think>', 1)[0].replace('<think>', '').strip(),
                        "answer": ''
                    }
                else:
                    answer_buf.append(delta)
                    yield {"reasoning": ''.join(reasoning_buf).split('</think>', 1)[0].replace('<think>\n', '').strip(),
                           "answer": ''.join(answer_buf).strip()}

    def close(self):
        """
        Cleanly shut down the server process.
        """
        if hasattr(self, 'proc') and self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
    
    def __del__(self):
        self.close()

if __name__ == "__main__":

    llm_model = LLMModel(model_name="Qwen3-0.6B-Q8_0", port=9527, timeout=30)
    print("LLM model server started successfully.")

    print("开始 stream_chat 流式输出：")

    for chunk in llm_model.stream_chat("你好啊朋友！"):
        reasoning, answer = chunk['reasoning'], chunk['answer']
        line = f"[思考] {reasoning}"
        if answer:
            line += f" [答案] {answer}"
        print(line, end='\r', flush=True)
        # reasoning = chunk.get("reasoning", "")
        # answer = chunk.get("answer", "")
        # if reasoning:
        #     print(f"[思考] {reasoning}")
        # if answer:
        #     print(f"[回复] {answer}")
    


