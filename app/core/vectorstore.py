import faiss
import json
import numpy as np
import logging
from pathlib import Path
from app.core.config import FAISS_INDEX_DIR

logger = logging.getLogger(__name__)

INDEX_PATH = FAISS_INDEX_DIR / "index.faiss"
META_PATH = FAISS_INDEX_DIR / "metadata.json"


class VectorStore:
    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.metadata = []

        try:
            if INDEX_PATH.exists():
                logger.info(f"Loading existing FAISS index from {INDEX_PATH}")
                self.index = faiss.read_index(str(INDEX_PATH))
                if META_PATH.exists():
                    self.metadata = json.loads(META_PATH.read_text())
                    logger.info(f"Loaded {len(self.metadata)} metadata entries")
                else:
                    logger.warning("Index exists but metadata.json not found")
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            raise

    def add(self, vectors, metadatas):
        """Add vectors and metadata to the store."""
        try:
            if not isinstance(vectors, np.ndarray):
                vectors = np.array(vectors, dtype="float32")
            else:
                vectors = vectors.astype("float32")
            
            if vectors.shape[1] != self.dim:
                raise ValueError(
                    f"Vector dimension mismatch: expected {self.dim}, got {vectors.shape[1]}"
                )
            
            self.index.add(vectors)
            self.metadata.extend(metadatas)
            logger.info(f"Added {len(vectors)} vectors to index")
            self.save()
        except Exception as e:
            logger.error(f"Error adding vectors: {e}")
            raise

    def save(self):
        """Save index and metadata to disk."""
        try:
            FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self.index, str(INDEX_PATH))
            META_PATH.write_text(json.dumps(self.metadata))
            logger.debug(f"Saved index to {INDEX_PATH}")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
            raise

    def search(self, vector: np.ndarray, k: int = 5):
        """
        Search for similar vectors.
        
        Args:
            vector: Query vector (1D array of shape (dim,))
            k: Number of results to return
            
        Returns:
            Tuple of (distances, indices)
        """
        try:
            if not isinstance(vector, np.ndarray):
                vector = np.array(vector, dtype="float32")
            else:
                vector = vector.astype("float32")
            
            # Reshape to 2D for FAISS (1, dim)
            v = vector.reshape(1, -1)
            distances, indices = self.index.search(v, k)

            # Filter out invalid indices and return valid pairs
            valid_indices = []
            valid_distances = []
            for i, idx in enumerate(indices[0]):
                if idx >= 0 and idx < len(self.metadata):
                    valid_indices.append(int(idx))
                    valid_distances.append(float(distances[0][i]))
            
            logger.debug(f"Search returned {len(valid_indices)} valid results")
            return valid_distances, valid_indices
        except Exception as e:
            logger.error(f"Error searching index: {e}")
            raise
