import faiss
import json
import numpy as np
from pathlib import Path

INDEX_PATH = Path("data/faiss_index/index.faiss")
META_PATH = Path("data/faiss_index/metadata.json")


class VectorStore:
    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.metadata = []

        if INDEX_PATH.exists():
            self.index = faiss.read_index(str(INDEX_PATH))
            self.metadata = json.loads(META_PATH.read_text())

    def add(self, vectors, metadatas):
        self.index.add(vectors)
        self.metadata.extend(metadatas)
        self.save()

    def save(self):
        faiss.write_index(self.index, str(INDEX_PATH))
        META_PATH.write_text(json.dumps(self.metadata))

    def search(self, vector: list[float], k: int = 5):
        v = np.array(vector, dtype="float32").reshape(1, -1)
        distances, indices = self.index.search(v, k)

        valid = [i for i in indices[0] if i < len(self.metadata)]
        return distances[0], valid
