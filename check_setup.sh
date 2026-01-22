#!/bin/bash

# 🔍 RAG Logistics - Quick Verification Script (Linux/Mac)
# Check if everything is ready before running the demo

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                ║${NC}"
echo -e "${BLUE}║           🔍 RAG System - Health Check                         ║${NC}"
echo -e "${BLUE}║                                                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

FAILED=0

# Check 1: venv
echo "[1/5] Checking Python virtual environment..."
if [ -f ".venv/bin/activate" ] || [ -f "/home/mabrouk/Bureau/.venv/bin/activate" ]; then
    echo -e "${GREEN}✅ Virtual environment found${NC}"
else
    echo -e "${RED}❌ Virtual environment not found - run: python -m venv .venv${NC}"
    FAILED=1
fi

# Check 2: frontend file
echo ""
echo "[2/5] Checking frontend application..."
if [ -f "frontend_rag_demo.html" ]; then
    SIZE=$(du -h frontend_rag_demo.html | cut -f1)
    echo -e "${GREEN}✅ frontend_rag_demo.html found ($SIZE)${NC}"
else
    echo -e "${RED}❌ frontend_rag_demo.html not found${NC}"
    FAILED=1
fi

# Check 3: backend
echo ""
echo "[3/5] Checking backend application..."
if [ -f "app/main.py" ]; then
    echo -e "${GREEN}✅ Backend application found${NC}"
else
    echo -e "${RED}❌ Backend application not found${NC}"
    FAILED=1
fi

# Check 4: FAISS index
echo ""
echo "[4/5] Checking FAISS vector index..."
if [ -f "data/faiss/index.faiss" ]; then
    SIZE=$(du -h data/faiss/index.faiss | cut -f1)
    echo -e "${GREEN}✅ FAISS index found ($SIZE)${NC}"
elif [ -f "data/faiss_index/index.faiss" ]; then
    SIZE=$(du -h data/faiss_index/index.faiss | cut -f1)
    echo -e "${GREEN}✅ FAISS index found - alternate location ($SIZE)${NC}"
else
    echo -e "${YELLOW}⚠️  FAISS index not found - may need to rebuild${NC}"
    echo "    Run: python setup_rag.py"
fi

# Check 5: test documents
echo ""
echo "[5/5] Checking test documents..."
if [ -d "data/raw_docs" ]; then
    DOC_COUNT=$(find data/raw_docs -name "*.txt" -type f | wc -l)
    if [ $DOC_COUNT -gt 0 ]; then
        echo -e "${GREEN}✅ Test documents found: $DOC_COUNT documents${NC}"
    else
        echo -e "${YELLOW}⚠️  No test documents found in data/raw_docs${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Test documents directory not found${NC}"
fi

echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                                                ║${NC}"
    echo -e "${BLUE}║              ✅ All Checks Passed!                            ║${NC}"
    echo -e "${BLUE}║                                                                ║${NC}"
    echo -e "${BLUE}║  You can now run: ./start_rag_demo.sh                         ║${NC}"
    echo -e "${BLUE}║                                                                ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
else
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                                                ║${NC}"
    echo -e "${RED}║              ❌ Setup Issue Detected                           ║${NC}"
    echo -e "${BLUE}║                                                                ║${NC}"
    echo -e "${BLUE}║  Please fix the above issues and try again                    ║${NC}"
    echo -e "${BLUE}║                                                                ║${NC}"
    echo -e "${BLUE}║  For help, see: FRONTEND_QUICKSTART.md                        ║${NC}"
    echo -e "${BLUE}║                                                                ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    exit 1
fi
