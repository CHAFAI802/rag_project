#!/usr/bin/env python3
"""
🚚 RAG Frontend Integration Verification
Comprehensive health check for frontend-backend integration
"""

import subprocess
import sys
import json
import time
from pathlib import Path

# Colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")

def check_mark(condition, text):
    status = f"{Colors.GREEN}✓{Colors.END}" if condition else f"{Colors.RED}✗{Colors.END}"
    print(f"  {status} {text}")
    return condition

def check_file_exists(path):
    """Check if required file exists"""
    exists = Path(path).exists()
    return check_mark(exists, f"File: {path}")

def check_api_health():
    """Check if API is running"""
    try:
        result = subprocess.run(
            ['curl', '-s', 'http://localhost:8000/health'],
            capture_output=True,
            timeout=2
        )
        if result.returncode == 0:
            return check_mark(True, "API health check: http://localhost:8000/health")
        return check_mark(False, "API health check failed")
    except Exception as e:
        return check_mark(False, f"API health check: {str(e)}")

def check_api_query():
    """Test API query endpoint"""
    try:
        payload = json.dumps({
            "question": "Quel est le délai maximal retard ?",
            "include_sources": True
        })
        result = subprocess.run(
            [
                'curl', '-s', '-X', 'POST',
                'http://localhost:8000/api/query',
                '-H', 'Content-Type: application/json',
                '-d', payload
            ],
            capture_output=True,
            timeout=5
        )
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                has_answer = 'answer' in response
                has_confidence = 'confidence' in response
                if has_answer and has_confidence:
                    conf = response['confidence']
                    return check_mark(True, f"API query endpoint: confidence={conf:.2f}")
            except:
                pass
        
        return check_mark(False, "API query endpoint failed")
    except Exception as e:
        return check_mark(False, f"API query test: {str(e)}")

def check_frontend_file():
    """Verify frontend file exists and has content"""
    frontend_path = Path('/home/mabrouk/Bureau/rag_project/frontend_rag_demo.html')
    if frontend_path.exists():
        size = frontend_path.stat().st_size
        has_api_call = 'fetch' in frontend_path.read_text()
        return check_mark(has_api_call, f"Frontend file: {size/1024:.1f} KB (with API client)")
    return check_mark(False, "Frontend file not found")

def check_faiss_index():
    """Check if FAISS vector index exists"""
    index_paths = [
        Path('/home/mabrouk/Bureau/rag_project/data/faiss/index.faiss'),
        Path('/home/mabrouk/Bureau/rag_project/data/faiss_index/index.faiss'),
    ]
    for path in index_paths:
        if path.exists():
            size = path.stat().st_size
            return check_mark(True, f"FAISS index found: {path.name} ({size/1024/1024:.1f} MB)")
    return check_mark(False, "FAISS index not found")

def check_test_documents():
    """Check if test documents are indexed"""
    doc_dir = Path('/home/mabrouk/Bureau/rag_project/data/raw_docs')
    if doc_dir.exists():
        docs = list(doc_dir.glob('*.txt'))
        return check_mark(len(docs) > 0, f"Test documents found: {len(docs)} documents")
    return check_mark(False, "Test documents directory not found")

def check_python_env():
    """Verify Python environment and dependencies"""
    try:
        result = subprocess.run(
            [sys.executable, '-c', 
             'import fastapi; import faiss; import langchain; print("OK")'],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            return check_mark(True, "Python dependencies: FastAPI, FAISS, LangChain ✓")
        return check_mark(False, "Missing Python dependencies")
    except Exception as e:
        return check_mark(False, f"Python environment check: {str(e)}")

def run_sample_queries():
    """Run sample queries from all three categories"""
    print(f"\n{Colors.YELLOW}Testing query samples:{Colors.END}\n")
    
    test_cases = [
        {
            "category": "A (Simple)",
            "question": "Quel est le délai maximal retard fournisseur ?",
            "min_confidence": 0.70
        },
        {
            "category": "B (Complex)",
            "question": "Quels sont les critères SLA fournisseur et coûts ?",
            "min_confidence": 0.60
        },
        {
            "category": "C (Hallucination)",
            "question": "Quel est le prix du Bitcoin ?",
            "max_confidence": 0.35
        }
    ]
    
    for test in test_cases:
        try:
            payload = json.dumps({
                "question": test["question"],
                "include_sources": True
            })
            result = subprocess.run(
                [
                    'curl', '-s', '-X', 'POST',
                    'http://localhost:8000/api/query',
                    '-H', 'Content-Type: application/json',
                    '-d', payload
                ],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                confidence = response.get('confidence', 0)
                
                if 'min_confidence' in test:
                    passed = confidence >= test['min_confidence']
                    check_mark(
                        passed,
                        f"Category {test['category']}: confidence={confidence:.2f} (need ≥{test['min_confidence']:.2f})"
                    )
                else:
                    passed = confidence <= test['max_confidence']
                    check_mark(
                        passed,
                        f"Category {test['category']}: confidence={confidence:.2f} (need ≤{test['max_confidence']:.2f})"
                    )
            else:
                check_mark(False, f"Category {test['category']}: Query failed")
        except Exception as e:
            check_mark(False, f"Category {test['category']}: {str(e)}")

def print_summary(all_passed):
    print_header("Integration Verification Summary")
    
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED{Colors.END}")
        print(f"\n{Colors.GREEN}Frontend is ready for demonstration!{Colors.END}\n")
        print(f"Access at: {Colors.BOLD}http://localhost:8001/frontend_rag_demo.html{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME CHECKS FAILED{Colors.END}")
        print(f"\n{Colors.YELLOW}Required actions:{Colors.END}")
        print(f"  1. Ensure API is running: {Colors.BOLD}python -m uvicorn app.main:app --port 8000{Colors.END}")
        print(f"  2. Verify Python environment: {Colors.BOLD}source .venv/bin/activate{Colors.END}")
        print(f"  3. Check FAISS index exists")

def main():
    print_header("🚚 RAG Frontend-Backend Integration Check")
    
    all_checks = []
    
    print(f"{Colors.YELLOW}File Checks:{Colors.END}\n")
    all_checks.append(check_frontend_file())
    all_checks.append(check_file_exists('/home/mabrouk/Bureau/rag_project/app/main.py'))
    all_checks.append(check_file_exists('/home/mabrouk/Bureau/rag_project/FRONTEND_QUICKSTART.md'))
    
    print(f"\n{Colors.YELLOW}Environment Checks:{Colors.END}\n")
    all_checks.append(check_python_env())
    all_checks.append(check_faiss_index())
    all_checks.append(check_test_documents())
    
    print(f"\n{Colors.YELLOW}API Checks:{Colors.END}\n")
    api_health = check_api_health()
    all_checks.append(api_health)
    
    if api_health:
        api_query = check_api_query()
        all_checks.append(api_query)
        
        if api_query:
            run_sample_queries()
    else:
        print(f"\n{Colors.YELLOW}API not running - skipping query tests{Colors.END}")
        print(f"To start API: {Colors.BOLD}python -m uvicorn app.main:app --port 8000{Colors.END}\n")
    
    # Summary
    all_passed = all(all_checks)
    print_summary(all_passed)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
