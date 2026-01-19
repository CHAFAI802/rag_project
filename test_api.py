"""
Test FastAPI endpoints for ingest and query.
"""
import asyncio
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    """Test health check endpoint."""
    print("\n" + "="*50)
    print("TEST: Health Check")
    print("="*50)
    
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print(f"✅ Health check passed: {data}")


def test_ingest_endpoint():
    """Test document ingestion endpoint."""
    print("\n" + "="*50)
    print("TEST: Ingest Endpoint")
    print("="*50)
    
    # Create test document
    test_content = """
    Python is a high-level programming language.
    It emphasizes code readability.
    Python supports multiple programming paradigms.
    """
    
    files = {"file": ("test_doc.txt", test_content, "text/plain")}
    
    response = client.post("/api/ingest", files=files)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_doc.txt"
    assert data["chars_extracted"] > 0
    assert data["status"] == "indexed"
    
    print("✅ Ingest endpoint test passed!")


def test_query_endpoint():
    """Test query endpoint."""
    print("\n" + "="*50)
    print("TEST: Query Endpoint")
    print("="*50)
    
    query_data = {"question": "What is Python?"}
    
    response = client.post("/api/query", json=query_data)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Answer (first 200 chars): {data['answer'][:200]}...")
        assert "answer" in data
        print("✅ Query endpoint test passed!")
    else:
        print(f"Error: {response.json()}")
        assert False, "Query failed"


def test_query_validation():
    """Test query validation."""
    print("\n" + "="*50)
    print("TEST: Query Validation")
    print("="*50)
    
    # Test empty question
    response = client.post("/api/query", json={"question": ""})
    print(f"Empty question status: {response.status_code}")
    assert response.status_code == 422  # Validation error
    
    # Test too long question
    response = client.post("/api/query", json={"question": "a" * 2000})
    print(f"Too long question status: {response.status_code}")
    assert response.status_code == 422  # Validation error
    
    print("✅ Query validation test passed!")


def main():
    """Run all API tests."""
    print("\n" + "🚀 TESTING RAG API ENDPOINTS 🚀" + "\n")
    
    tests = [
        ("Health", test_health),
        ("Ingest", test_ingest_endpoint),
        ("Query", test_query_endpoint),
        ("Validation", test_query_validation),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, True))
        except Exception as e:
            print(f"\n❌ {name} test failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "="*50)
    print("API TEST SUMMARY")
    print("="*50)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 ALL API TESTS PASSED! 🎉")
        return 0
    else:
        print("\n⚠️  SOME API TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
