#!/bin/bash

# 🚚 RAG Logistics Frontend - Startup Script (Linux/Mac)
# This script starts both the API and Frontend servers in separate terminals

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                ║${NC}"
echo -e "${BLUE}║          🚚 RAG Logistics - Frontend Demo Startup              ║${NC}"
echo -e "${BLUE}║                                                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if venv exists
if [ ! -d ".venv" ] && [ ! -d "/home/mabrouk/Bureau/.venv" ]; then
    echo -e "${RED}❌ ERROR: Virtual environment not found${NC}"
    echo ""
    echo "Please create it first:"
    echo "  python -m venv .venv"
    echo ""
    exit 1
fi

# Check if frontend file exists
if [ ! -f "frontend_rag_demo.html" ]; then
    echo -e "${RED}❌ ERROR: frontend_rag_demo.html not found${NC}"
    echo ""
    echo "Please ensure you're in the rag_project directory"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Starting RAG Logistics Demo...${NC}"
echo ""
echo "Starting API Server (Port 8000)..."
echo "Starting Frontend Server (Port 8001)..."
echo ""
sleep 1

# Activate venv - find it in either location
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "/home/mabrouk/Bureau/.venv/bin/activate" ]; then
    source /home/mabrouk/Bureau/.venv/bin/activate
else
    echo -e "${RED}❌ Could not find virtual environment${NC}"
    exit 1
fi

# Function to kill processes on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Cleaning up...${NC}"
    kill $API_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
}

trap cleanup EXIT

# Find and activate venv
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "/home/mabrouk/Bureau/.venv/bin/activate" ]; then
    source /home/mabrouk/Bureau/.venv/bin/activate
else
    echo -e "${RED}❌ Could not find virtual environment${NC}"
    exit 1
fi

# Start API server in background
echo -e "${GREEN}Starting API server...${NC}"
python -m uvicorn app.main:app --port 8000 --reload &
API_PID=$!
sleep 2

# Start Frontend server in background
echo -e "${GREEN}Starting frontend server...${NC}"
python -m http.server 8001 --directory . &
FRONTEND_PID=$!
sleep 1

# Open browser if available
if command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open http://localhost:8001/frontend_rag_demo.html
elif command -v open &> /dev/null; then
    # macOS
    open http://localhost:8001/frontend_rag_demo.html
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                ║${NC}"
echo -e "${BLUE}║              ✅ Servers Running!                               ║${NC}"
echo -e "${BLUE}║                                                                ║${NC}"
echo -e "${BLUE}║  API Server:      ${GREEN}http://localhost:8000${BLUE}                    ║${NC}"
echo -e "${BLUE}║  Frontend:        ${GREEN}http://localhost:8001/frontend_rag_demo.html${NC}${BLUE} ║${NC}"
echo -e "${BLUE}║  Swagger UI:      ${GREEN}http://localhost:8000/docs${BLUE}                 ║${NC}"
echo -e "${BLUE}║                                                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📝 Both servers are running in the background${NC}"
echo ""
echo "💡 Tips:"
echo "   - Check API: curl http://localhost:8000/health"
echo "   - View logs: Check the terminal output above"
echo "   - Stop: Press Ctrl+C to stop both servers"
echo ""

# Keep the script running
wait
