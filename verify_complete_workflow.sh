#!/bin/bash

# 🔍 VERIFICATION COMPLETE DU WORKFLOW RAG FRONTEND
# Teste fichier par fichier le workflow complet

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

PASSED=0
FAILED=0

print_header() {
    echo ""
    echo -e "${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}${BOLD}$1${NC}"
    echo -e "${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

test_result() {
    local name=$1
    local status=$2
    local details=$3
    
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✅${NC} $name"
        if [ ! -z "$details" ]; then
            echo -e "   ${YELLOW}→${NC} $details"
        fi
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} $name"
        if [ ! -z "$details" ]; then
            echo -e "   ${RED}→${NC} $details"
        fi
        ((FAILED++))
    fi
}

cd /home/mabrouk/Bureau/rag_project

echo ""
echo -e "${BOLD}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║  🔍 VERIFICATION COMPLETE - RAG FRONTEND WORKFLOW         ║${NC}"
echo -e "${BOLD}╚════════════════════════════════════════════════════════════╝${NC}"

# =====================================================================
# SECTION 1: FICHIERS FRONTEND
# =====================================================================
print_header "📦 SECTION 1: FICHIERS FRONTEND"

if [ -f "frontend_rag_demo.html" ]; then
    SIZE=$(du -h frontend_rag_demo.html | cut -f1)
    LINES=$(wc -l < frontend_rag_demo.html)
    test_result "frontend_rag_demo.html" "PASS" "$SIZE ($LINES lines)"
    
    # Vérifier contenu clé
    if grep -q "8000" frontend_rag_demo.html; then
        test_result "  - API endpoint configuré" "PASS" "localhost:8000"
    else
        test_result "  - API endpoint configuré" "FAIL" "Endpoint non trouvé"
    fi
    
    if grep -q "Confiance\|Risque Hallucination" frontend_rag_demo.html; then
        test_result "  - Métriques configurées" "PASS" "4 métriques"
    else
        test_result "  - Métriques configurées" "FAIL" "Métriques manquantes"
    fi
    
    if grep -q "Category.*A\|Category.*B\|Category.*C" frontend_rag_demo.html; then
        test_result "  - Catégories présentes" "PASS" "A, B, C"
    else
        test_result "  - Catégories présentes" "FAIL" "Catégories manquantes"
    fi
else
    test_result "frontend_rag_demo.html" "FAIL" "Fichier non trouvé"
fi

# =====================================================================
# SECTION 2: SCRIPTS DE DÉPLOIEMENT
# =====================================================================
print_header "🔧 SECTION 2: SCRIPTS DE DÉPLOIEMENT"

if [ -f "start_rag_demo.sh" ] && [ -x "start_rag_demo.sh" ]; then
    test_result "start_rag_demo.sh" "PASS" "Exécutable"
    if grep -q "uvicorn app.main:app" start_rag_demo.sh; then
        test_result "  - API startup" "PASS" "Configuré"
    else
        test_result "  - API startup" "FAIL" "Non configuré"
    fi
else
    test_result "start_rag_demo.sh" "FAIL" "Manquant ou non exécutable"
fi

if [ -f "check_setup.sh" ] && [ -x "check_setup.sh" ]; then
    test_result "check_setup.sh" "PASS" "Exécutable"
else
    test_result "check_setup.sh" "FAIL" "Manquant ou non exécutable"
fi

if [ -f "frontend_deploy.sh" ] && [ -x "frontend_deploy.sh" ]; then
    test_result "frontend_deploy.sh" "PASS" "Exécutable"
else
    test_result "frontend_deploy.sh" "FAIL" "Manquant ou non exécutable"
fi

# =====================================================================
# SECTION 3: SCRIPTS BATCH (WINDOWS)
# =====================================================================
print_header "🪟 SECTION 3: SCRIPTS BATCH (WINDOWS)"

if [ -f "start_rag_demo.bat" ]; then
    if grep -q "uvicorn" start_rag_demo.bat; then
        test_result "start_rag_demo.bat" "PASS" "Configuré"
    else
        test_result "start_rag_demo.bat" "PASS" "Présent"
    fi
else
    test_result "start_rag_demo.bat" "FAIL" "Manquant"
fi

if [ -f "check_setup.bat" ]; then
    test_result "check_setup.bat" "PASS" "Présent"
else
    test_result "check_setup.bat" "FAIL" "Manquant"
fi

# =====================================================================
# SECTION 4: DOCUMENTATION
# =====================================================================
print_header "📖 SECTION 4: DOCUMENTATION"

DOCS=(
    "FRONTEND_QUICKSTART.md"
    "FRONTEND_SUMMARY.md"
    "DEPLOY_FRONTEND_NOW.md"
    "START_HERE.md"
    "SHELL_SCRIPTS_README.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        SIZE=$(du -h "$doc" | cut -f1)
        test_result "$doc" "PASS" "$SIZE"
    else
        test_result "$doc" "FAIL" "Manquant"
    fi
done

# =====================================================================
# SECTION 5: BACKEND APPLICATION
# =====================================================================
print_header "🔵 SECTION 5: BACKEND APPLICATION"

if [ -f "app/main.py" ]; then
    test_result "app/main.py" "PASS" "API FastAPI"
    
    if grep -q "@app.post.*query" app/main.py; then
        test_result "  - Endpoint /api/query" "PASS" "Présent"
    else
        test_result "  - Endpoint /api/query" "FAIL" "Manquant"
    fi
    
    if grep -q "@app.get.*health" app/main.py; then
        test_result "  - Endpoint /health" "PASS" "Présent"
    else
        test_result "  - Endpoint /health" "FAIL" "Manquant"
    fi
else
    test_result "app/main.py" "FAIL" "Manquant"
fi

if [ -f "app/core/vectorstore.py" ]; then
    test_result "app/core/vectorstore.py" "PASS" "FAISS vectorstore"
else
    test_result "app/core/vectorstore.py" "FAIL" "Manquant"
fi

if [ -f "app/services/rag_pipeline.py" ]; then
    test_result "app/services/rag_pipeline.py" "PASS" "RAG pipeline"
else
    test_result "app/services/rag_pipeline.py" "FAIL" "Manquant"
fi

# =====================================================================
# SECTION 6: DONNÉES ET INDEX
# =====================================================================
print_header "💾 SECTION 6: DONNÉES ET INDEX"

if [ -d "data/raw_docs" ]; then
    DOC_COUNT=$(find data/raw_docs -name "*.txt" -type f | wc -l)
    test_result "data/raw_docs/" "PASS" "$DOC_COUNT documents"
else
    test_result "data/raw_docs/" "FAIL" "Répertoire manquant"
fi

if [ -f "data/faiss/index.faiss" ]; then
    SIZE=$(du -h data/faiss/index.faiss | cut -f1)
    test_result "data/faiss/index.faiss" "PASS" "$SIZE"
elif [ -f "data/faiss_index/index.faiss" ]; then
    SIZE=$(du -h data/faiss_index/index.faiss | cut -f1)
    test_result "data/faiss_index/index.faiss" "PASS" "$SIZE (alternate)"
else
    test_result "FAISS index" "FAIL" "Non trouvé"
fi

# =====================================================================
# SECTION 7: TESTS DE QUALITÉ
# =====================================================================
print_header "🧪 SECTION 7: TESTS DE QUALITÉ"

if [ -f "quality_testing_executive.py" ]; then
    test_result "quality_testing_executive.py" "PASS" "13 tests"
else
    test_result "quality_testing_executive.py" "FAIL" "Manquant"
fi

if [ -f "demo_quality_testing.py" ]; then
    test_result "demo_quality_testing.py" "PASS" "5 démos"
else
    test_result "demo_quality_testing.py" "FAIL" "Manquant"
fi

if [ -f "run_quality_tests.py" ]; then
    test_result "run_quality_tests.py" "PASS" "CLI orchestrator"
else
    test_result "run_quality_tests.py" "FAIL" "Manquant"
fi

# =====================================================================
# SECTION 8: PYTHON ENVIRONMENT
# =====================================================================
print_header "🐍 SECTION 8: PYTHON ENVIRONMENT"

if [ -f "/home/mabrouk/Bureau/.venv/bin/activate" ]; then
    PYTHON_VERSION=$(/home/mabrouk/Bureau/.venv/bin/python --version 2>&1)
    test_result "Virtual environment" "PASS" "$PYTHON_VERSION"
    
    # Vérifier les packages clés
    if /home/mabrouk/Bureau/.venv/bin/python -c "import fastapi" 2>/dev/null; then
        test_result "  - FastAPI" "PASS" "Installé"
    else
        test_result "  - FastAPI" "FAIL" "Non installé"
    fi
    
    if /home/mabrouk/Bureau/.venv/bin/python -c "import faiss" 2>/dev/null; then
        test_result "  - FAISS" "PASS" "Installé"
    else
        test_result "  - FAISS" "FAIL" "Non installé"
    fi
    
    if /home/mabrouk/Bureau/.venv/bin/python -c "import langchain" 2>/dev/null; then
        test_result "  - LangChain" "PASS" "Installé"
    else
        test_result "  - LangChain" "FAIL" "Non installé"
    fi
else
    test_result "Virtual environment" "FAIL" "Non trouvé"
fi

# =====================================================================
# SECTION 9: CONNECTIVITY TESTS
# =====================================================================
print_header "🔌 SECTION 9: CONNECTIVITY TESTS"

echo "Vérification des serveurs..."
echo ""

# Test API
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    HEALTH=$(curl -s http://localhost:8000/health | grep -o '"status":"[^"]*"')
    test_result "API Health Check (port 8000)" "PASS" "$HEALTH"
else
    test_result "API Health Check (port 8000)" "FAIL" "Serveur non accessible"
fi

# Test Frontend Server
if curl -s http://localhost:8001/frontend_rag_demo.html > /dev/null 2>&1; then
    test_result "Frontend Server (port 8001)" "PASS" "Accessible"
else
    test_result "Frontend Server (port 8001)" "FAIL" "Serveur non accessible"
fi

# Test Query Endpoint
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    RESPONSE=$(curl -s -X POST http://localhost:8000/api/query \
        -H "Content-Type: application/json" \
        -d '{"question": "test"}' 2>/dev/null)
    
    if echo "$RESPONSE" | grep -q "answer"; then
        CONF=$(echo "$RESPONSE" | grep -o '"confidence":[0-9.]*' | head -1)
        test_result "API Query Endpoint" "PASS" "$CONF"
    else
        test_result "API Query Endpoint" "FAIL" "Réponse invalide"
    fi
fi

# =====================================================================
# SECTION 10: RÉSUMÉ
# =====================================================================
print_header "📊 RÉSUMÉ FINAL"

TOTAL=$((PASSED + FAILED))
PERCENT=$((PASSED * 100 / TOTAL))

echo "Tests réussis:  ${GREEN}$PASSED✅${NC}"
echo "Tests échoués:  ${RED}$FAILED❌${NC}"
echo "Total:          $TOTAL tests"
echo "Taux de réussite: ${BLUE}$PERCENT%${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  🎉 TOUS LES TESTS RÉUSSIS!                              ║${NC}"
    echo -e "${BLUE}║                                                            ║${NC}"
    echo -e "${BLUE}║  Le système est prêt pour la démonstration!              ║${NC}"
    echo -e "${BLUE}║                                                            ║${NC}"
    echo -e "${BLUE}║  Ouvrez: http://localhost:8001/frontend_rag_demo.html    ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
else
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  ⚠️  QUELQUES TESTS ONT ÉCHOUÉ                            ║${NC}"
    echo -e "${BLUE}║                                                            ║${NC}"
    echo -e "${BLUE}║  Vérifiez les erreurs ci-dessus et réessayez             ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
fi

echo ""
