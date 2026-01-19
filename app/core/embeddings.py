import os
import numpy as np
from typing import Union
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from numpy.typing import NDArray
from app.core.config import HF_TOKEN, EMBEDDING_MODEL

load_dotenv()

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN manquant")

client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN,
)

def embed_texts(texts: list[str]) -> NDArray:
    """
    Embed a list of texts using HuggingFace Inference API.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        numpy array of shape (len(texts), 384) with float32 dtype
    """
    result = client.feature_extraction(
        texts,
        model=EMBEDDING_MODEL
    )
    return np.array(result, dtype="float32")


def embed_query(question: str) -> NDArray:
    """
    Embed a single query string.
    
    Args:
        question: Query string to embed
        
    Returns:
        numpy array of shape (384,) with float32 dtype
    """
    result = client.feature_extraction(
        [question],
        model=EMBEDDING_MODEL
    )
    return np.array(result[0], dtype="float32")
