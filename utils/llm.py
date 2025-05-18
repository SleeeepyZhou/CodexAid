import requests
import os, sys
currunt_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(currunt_dir, ".."))
from config import LLM

class LLMModel:
    def __init__(
            self, 
            model_name: str = "gpt-4o-mini",
            timeout: int = 30
        ):
        self.model_name = model_name
        self.timeout = timeout

        self.url = LLM["url"]
        self.header = {
            "Authorization": f"Bearer {LLM['key']}",
            "Content-Type": "application/json"
        }

    def dialogue(self, messages, **params) -> dict:
        params.pop('stream', None)
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            **params
        }
        resp = requests.post(self.url, json=payload, headers=self.header, timeout=self.timeout)
        resp.raise_for_status()
        response = resp.json()
        return {
            "reasoning": response["choices"][0]["message"].get("reasoning_content"),
            "answer": response["choices"][0]["message"].get("content")
        }

    def chat(self, prompt: str, role: str = "user", **params) -> dict:
        """
        Standard chat completion.
        messages: list of {"role": ..., "content": ...}
        params: other OpenAI parameters (e.g., max_tokens)
        """
        messages = [{"role": role, "content": prompt}]
        return self.dialogue(messages, **params)

    def close(self):
        pass
    
    def __del__(self):
        self.close()


if __name__ == "__main__":

    llm_model = LLMModel()
    print("LLM model server started successfully.")
    result = llm_model.chat("你好！")
    print(result["answer"])

    # print("开始 stream_chat 流式输出：")

    # for chunk in llm_model.stream_chat("你好啊朋友！"):
    #     reasoning, answer = chunk['reasoning'], chunk['answer']
    #     line = f"[思考] {reasoning}"
    #     if answer:
    #         line += f" [答案] {answer}"
    #     print(line, end='\r', flush=True)
    #     reasoning = chunk.get("reasoning", "")
    #     answer = chunk.get("answer", "")
    #     if reasoning:
    #         print(f"[思考] {reasoning}")
    #     if answer:
    #         print(f"[回复] {answer}")
