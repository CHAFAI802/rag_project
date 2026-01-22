from pathlib import Path
import os
from dotenv import load_dotenv

# Charger le fichier .env
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# ======================
# Hugging Face
# ======================
HF_TOKEN = os.getenv("HF_TOKEN")
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "sentence-transformers/all-MiniLM-L6-v2"
)

# ======================
# Chunking
# ======================
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))

# ======================
# Vector Store
# ======================
VECTOR_DIMENSION = int(os.getenv("VECTOR_DIMENSION", 384))
VECTOR_STORE_PATH = BASE_DIR / "vector_store"
RAW_DOCS_DIR = BASE_DIR / "data" / "raw_docs"
FAISS_INDEX_DIR = BASE_DIR / "data" / "faiss_index"

# Ensure directories exist
RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)

# Aliases for common usage
EMBEDDING_MODEL = EMBEDDING_MODEL_NAME
EMBEDDING_DIM = VECTOR_DIMENSION
K_RESULTS = 5
# Use distilgpt2 with optimized parameters for accurate answers
LLM_MODEL = "distilgpt2"  # Lightweight model (~340MB, fits in 4GB RAM)
LLM_MAX_TOKENS = 150  # Reduced to force concise, focused answers
LLM_TEMPERATURE = 0.2  # Very low temperature for factual, deterministic answers

# ======================
# Sanity checks
# ======================
if HF_TOKEN is None:
    raise RuntimeError("HF_TOKEN manquant. Vérifie ton fichier .env")
