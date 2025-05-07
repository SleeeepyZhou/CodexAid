import os
from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.normpath(os.path.join(current_dir, "..", "models", "all-MiniLM-L6-v2"))
        model_path = model_path.replace("\\", "/")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model path does not exist: {model_path}")
        
        self.model = SentenceTransformer(model_path, local_files_only=True)

    def embed(self, sentences: str) -> list[float]:
        vec = self.model.encode(sentences)
        vec_list = vec.tolist()
        return vec_list

if __name__ == "__main__":
    sentences = "This is an example sentence"
    embedding_model = EmbeddingModel()
    embeddings = embedding_model.embed(sentences)
    print(embeddings)
