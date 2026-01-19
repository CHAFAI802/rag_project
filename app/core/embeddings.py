import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN manquant")

client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN,
)

def embed_texts(texts: list[str]) -> list[list[float]]:
    return client.feature_extraction(
        texts,
        model=MODEL_NAME
    )
