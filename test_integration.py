"""
Integration test for RAG pipeline.
Tests document ingestion and query workflow.
"""
import tempfile
import shutil
from pathlib import Path
import numpy as np

# Import services
from app.services.document_loader import load_document
from app.services.chunker import chunk_text
from app.services.rag_pipeline import index_document, query_rag
from app.core.vectorstore import VectorStore
from app.core.embeddings import embed_texts, embed_query


def test_chunking():
    """Test chunking functionality."""
    print("\n" + "="*50)
    print("TEST 1: Document Chunking")
    print("="*50)
    
    text = "This is a test document. " * 100  # ~2500 chars
    chunks = chunk_text(text, chunk_size=500, overlap=100)
    
    print(f"Document length: {len(text)} chars")
    print(f"Number of chunks: {len(chunks)}")
    print(f"First chunk (100 chars): {chunks[0][:100]}...")
    
    assert len(chunks) > 0, "No chunks created"
    assert len(chunks[0]) <= 500, "Chunk too large"
    print("✅ Chunking test passed!")
    return True


def test_vectorstore():
    """Test VectorStore functionality."""
    print("\n" + "="*50)
    print("TEST 2: Vector Store")
    print("="*50)
    
    try:
        # Create test vectors (use predictable ones, not random)
        base_vec = np.array([1.0] * 384, dtype="float32")
        base_vec = base_vec / np.linalg.norm(base_vec)
        
        test_vectors = np.array([
            base_vec,  # Most similar to query (itself)
            base_vec * 0.9,  # Less similar
            base_vec * 0.7,  # Even less similar
            np.random.randn(384).astype("float32"),  # Random
            np.random.randn(384).astype("float32"),  # Random
        ], dtype="float32")
        
        test_metadata = [
            {"text": f"Document {i}", "source": "test.txt"}
            for i in range(5)
        ]
        
        # Initialize store
        store = VectorStore(384)
        print(f"Initialized VectorStore with dimension 384")
        
        # Add vectors
        store.add(test_vectors, test_metadata)
        print(f"Added {len(test_vectors)} vectors")
        
        # Search
        query_vec = test_vectors[0]  # Use first vector as query
        distances, indices = store.search(query_vec, k=3)
        
        print(f"Search returned {len(indices)} results")
        print(f"Top result indices: {indices}")
        print(f"Distances: {distances}")
        
        assert len(indices) > 0, "No search results"
        assert indices[0] == 0, "First vector should be most similar to itself"
        
        print("✅ VectorStore test passed!")
        return True
    except Exception as e:
        print(f"❌ VectorStore test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_pipeline():
    """Test full RAG pipeline with a sample document."""
    print("\n" + "="*50)
    print("TEST 3: Full RAG Pipeline")
    print("="*50)
    
    try:
        # Create temporary test document
        test_text = """
        Python is a popular programming language.
        It is known for its simplicity and readability.
        Python is widely used in web development, data science, and AI.
        The language has a large community and many useful libraries.
        """
        
        # Test indexing
        print("Indexing document...")
        index_document(test_text, "test_doc.txt")
        print("✅ Document indexed successfully")
        
        # Test querying
        print("Processing query...")
        answer = query_rag("What is Python used for?")
        print(f"Answer: {answer[:200]}...")
        
        assert len(answer) > 0, "No answer generated"
        assert "No documents indexed" not in answer, "Index appears empty"
        
        print("✅ Full pipeline test passed!")
        return True
    except Exception as e:
        print(f"❌ Full pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "🧪 RUNNING RAG PIPELINE INTEGRATION TESTS 🧪" + "\n")
    
    results = []
    
    try:
        results.append(("Chunking", test_chunking()))
    except Exception as e:
        print(f"❌ Chunking test error: {e}")
        results.append(("Chunking", False))
    
    try:
        results.append(("VectorStore", test_vectorstore()))
    except Exception as e:
        print(f"❌ VectorStore test error: {e}")
        results.append(("VectorStore", False))
    
    try:
        results.append(("Full Pipeline", test_full_pipeline()))
    except Exception as e:
        print(f"❌ Full Pipeline test error: {e}")
        results.append(("Full Pipeline", False))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
