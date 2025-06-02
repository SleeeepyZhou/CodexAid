import requests
import os, sys
currunt_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(currunt_dir, ".."))
from config import LLM

class LLMModel:
    def __init__(
            self, 
            model_name: str = "Qwen/Qwen3-8B",
            timeout: int = 30,
            url: str = LLM["url"],
            key: str = LLM["key"]
        ):
        self.model_name = model_name
        self.timeout = timeout

        self.url = url
        self.header = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

    def dialogue(self, messages, **params) -> dict:
        params.pop('stream', None)
        payload = {
            "model": self.model_name,
            "response_format": {"type": "json_object"},
            "messages": messages,
            "stream": False,
            **params
        }
        try:
            resp = requests.post(self.url, json=payload, headers=self.header, timeout=self.timeout)
            resp.raise_for_status()
            response = resp.json()
            return {
                "reasoning": response["choices"][0]["message"].get("reasoning_content"),
                "answer": response["choices"][0]["message"].get("content")
            }
        except requests.exceptions.RequestException as e:
            return {"reasoning": None, "answer": None}

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
