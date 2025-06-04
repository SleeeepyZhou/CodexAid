import requests

import os, sys
currunt_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(currunt_dir, ".."))
from config import EMBEDDING

class EmbeddingModel:
    def __init__(self):
        self.url = EMBEDDING["url"]
        self.header = {
                        "Authorization": f"Bearer {EMBEDDING['key']}",
                        "Content-Type": "application/json"
                    }

    def embed(self, sentences: str) -> list:
        payload = {
            "model": "BAAI/bge-m3",
            "input": sentences,
            "encoding_format": "float"
        }
        response = requests.request("POST", self.url, json=payload, headers=self.header)
        vec = response.json()
        vec_list = vec["data"][0]["embedding"]
        return vec_list

if __name__ == "__main__":
    sentences = "This is an example sentence"
    embedding_model = EmbeddingModel()
    embeddings = embedding_model.embed(sentences)
    print(len(embeddings))

