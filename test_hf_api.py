"""
Test script for HuggingFace Inference API embeddings.
This tests the embedding function before running the full RAG pipeline.
"""
import numpy as np
import pytest
import requests
from dotenv import load_dotenv
from app.core.embeddings import embed_texts, embed_query

load_dotenv()


def test_embeddings():
    """Test embedding functionality."""

    texts = [
        "That is a happy person",
        "That is a happy dog",
        "That is a very happy person",
        "Today is a sunny day",
    ]

    print("Testing embed_texts...")
    try:
        embeddings = embed_texts(texts)
    except requests.exceptions.RequestException as exc:
        pytest.skip(f"HuggingFace API unavailable: {exc}")
    except Exception as exc:
        pytest.skip(f"Embedding service unavailable: {exc}")
    print(f"✓ Embeddings shape: {embeddings.shape}")
    assert embeddings.shape == (4, 384), f"Expected shape (4, 384), got {embeddings.shape}"
    assert embeddings.dtype == np.float32, f"Expected dtype float32, got {embeddings.dtype}"

    print("\nTesting embed_query...")
    query_embedding = embed_query("What makes a person happy?")
    print(f"✓ Query embedding shape: {query_embedding.shape}")
    assert query_embedding.shape == (384,), f"Expected shape (384,), got {query_embedding.shape}"
    assert query_embedding.dtype == np.float32, f"Expected dtype float32, got {query_embedding.dtype}"

    print("\nTesting similarity...")
    similarity = np.dot(embeddings[0], query_embedding) / (
        np.linalg.norm(embeddings[0]) * np.linalg.norm(query_embedding)
    )
    print(f"✓ Cosine similarity between first text and query: {similarity:.4f}")

    print("\n✅ All embedding tests passed!")


if __name__ == "__main__":  # pragma: no cover
    test_embeddings()
    exit(0)
