"""
Test script for HuggingFace Inference API embeddings.
This tests the embedding function before running the full RAG pipeline.
"""
import os
import numpy as np
from dotenv import load_dotenv
from app.core.embeddings import embed_texts, embed_query

load_dotenv()

def test_embeddings():
    """Test embedding functionality."""
    try:
        # Test embed_texts
        texts = [
            "That is a happy person",
            "That is a happy dog",
            "That is a very happy person",
            "Today is a sunny day"
        ]
        
        print("Testing embed_texts...")
        embeddings = embed_texts(texts)
        print(f"✓ Embeddings shape: {embeddings.shape}")
        assert embeddings.shape == (4, 384), f"Expected shape (4, 384), got {embeddings.shape}"
        assert embeddings.dtype == np.float32, f"Expected dtype float32, got {embeddings.dtype}"
        
        # Test embed_query
        print("\nTesting embed_query...")
        query_embedding = embed_query("What makes a person happy?")
        print(f"✓ Query embedding shape: {query_embedding.shape}")
        assert query_embedding.shape == (384,), f"Expected shape (384,), got {query_embedding.shape}"
        assert query_embedding.dtype == np.float32, f"Expected dtype float32, got {query_embedding.dtype}"
        
        # Simple similarity check (cosine similarity)
        print("\nTesting similarity...")
        similarity = np.dot(embeddings[0], query_embedding) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(query_embedding)
        )
        print(f"✓ Cosine similarity between first text and query: {similarity:.4f}")
        
        print("\n✅ All embedding tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_embeddings()
    exit(0 if success else 1)
