#!/usr/bin/env bash
# 🚚 RAG Frontend Deployment Guide
# Simple deployment scripts for the demo frontend

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🚚 RAG Logistics - Frontend Deployment Guide${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}\n"

# Functions
start_dev_server() {
    echo -e "${YELLOW}Starting development server...${NC}\n"
    
    # Simple Python HTTP server
    echo -e "${GREEN}✓ Frontend available at: ${BLUE}http://localhost:8001${NC}\n"
    python -m http.server 8001 --bind 127.0.0.1 --directory /home/mabrouk/Bureau/rag_project
}

start_with_backend() {
    echo -e "${YELLOW}Starting RAG API backend...${NC}"
    cd /home/mabrouk/Bureau/rag_project
    
    # Activate venv
    source .venv/bin/activate
    
    # Start API
    echo -e "${GREEN}✓ API starting on http://localhost:8000${NC}"
    echo -e "${YELLOW}In another terminal, run:${NC}"
    echo -e "  ${BLUE}cd /home/mabrouk/Bureau/rag_project${NC}"
    echo -e "  ${BLUE}python -m http.server 8001 --directory .${NC}\n"
    
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

show_endpoints() {
    echo -e "${BLUE}API Endpoints:${NC}\n"
    echo -e "  ${GREEN}POST${NC} /api/query"
    echo -e "    └─ Query with sources and confidence scores"
    echo -e "    └─ Payload: {\"question\": \"string\", \"include_sources\": true}\n"
    
    echo -e "  ${GREEN}POST${NC} /api/query-simple"
    echo -e "    └─ Simple query (answer only)"
    echo -e "    └─ Payload: {\"question\": \"string\"}\n"
    
    echo -e "  ${GREEN}GET${NC} /health"
    echo -e "    └─ Health check\n"
    
    echo -e "  ${GREEN}GET${NC} /docs"
    echo -e "    └─ Swagger UI (when API is running)\n"
}

show_usage() {
    cat << EOF

${BLUE}USAGE:${NC}
  bash frontend_deploy.sh [command]

${BLUE}COMMANDS:${NC}
  dev         Start development server (frontend only on port 8001)
  backend     Start backend API (port 8000)
  full        Start both (needs two terminals)
  test        Test API connectivity
  endpoints   Show API endpoints
  help        Show this help

${BLUE}QUICK START:${NC}
  
  Terminal 1 - Start Backend:
    cd /home/mabrouk/Bureau/rag_project
    source .venv/bin/activate
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  
  Terminal 2 - Start Frontend:
    cd /home/mabrouk/Bureau/rag_project
    python -m http.server 8001 --directory .
  
  Then open: ${BLUE}http://localhost:8001/frontend_rag_demo.html${NC}

${BLUE}DOCKER DEPLOYMENT:${NC}
  
  Build: docker build -t rag-logistics .
  Run:   docker-compose up -d
  
  Access frontend at: http://localhost:8001

${BLUE}NOTES:${NC}
  • Frontend is a static HTML file - no build step needed
  • Requires API running on http://localhost:8000
  • CORS enabled in API for local development
  • Three query examples in UI (Category A, B, C)

EOF
}

test_api() {
    echo -e "${YELLOW}Testing API connectivity...${NC}\n"
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API is running${NC}"
        echo -e "  Health: $(curl -s http://localhost:8000/health | jq .status)"
    else
        echo -e "${RED}✗ API is not running${NC}"
        echo -e "  Start it with: ${BLUE}python -m uvicorn app.main:app --port 8000${NC}"
        return 1
    fi
    
    echo -e "\n${YELLOW}Testing /query endpoint...${NC}\n"
    
    RESPONSE=$(curl -s -X POST http://localhost:8000/api/query \
        -H "Content-Type: application/json" \
        -d '{"question": "Quel est le délai maximal retard ?"}')
    
    if echo "$RESPONSE" | jq -e '.answer' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Query endpoint working${NC}"
        echo -e "  Answer: $(echo "$RESPONSE" | jq -r '.answer' | head -c 100)..."
        echo -e "  Confidence: $(echo "$RESPONSE" | jq -r '.confidence')"
    else
        echo -e "${RED}✗ Query endpoint error${NC}"
        echo -e "  Response: $RESPONSE"
        return 1
    fi
}

# Parse arguments
case "${1:-help}" in
    dev)
        start_dev_server
        ;;
    backend)
        start_with_backend
        ;;
    full)
        echo -e "${YELLOW}To run both frontend and backend:${NC}\n"
        echo -e "${BLUE}Terminal 1:${NC}"
        echo -e "  cd /home/mabrouk/Bureau/rag_project"
        echo -e "  source .venv/bin/activate"
        echo -e "  python -m uvicorn app.main:app --port 8000 --reload\n"
        echo -e "${BLUE}Terminal 2:${NC}"
        echo -e "  cd /home/mabrouk/Bureau/rag_project"
        echo -e "  python -m http.server 8001 --directory .\n"
        echo -e "${BLUE}Then open:${NC}"
        echo -e "  http://localhost:8001/frontend_rag_demo.html\n"
        ;;
    test)
        test_api
        ;;
    endpoints)
        show_endpoints
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        show_usage
        exit 1
        ;;
esac
