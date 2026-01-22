# 🚚 RAG Quality Testing & Demonstration
## Logistics Integration Use Case - Executive Summary

---

## 📋 Overview

This quality testing framework validates that the RAG system is:
- ✅ **Reliable** - High accuracy on domain questions
- ✅ **Traceable** - Full source attribution with confidence scores  
- ✅ **Non-Hallucinated** - Refuses to answer out-of-corpus questions
- ✅ **ERP-Ready** - Structured JSON responses for integration
- ✅ **Enterprise-Grade** - Suitable for C-suite review

---

## 🎯 Quick Start

### 1. Setup: Index Documents
```bash
cd /home/mabrouk/Bureau/rag_project
source .venv/bin/activate

# Index all logistics documents
python setup_rag.py
```

**Expected Output:**
```
SETTING UP RAG VECTOR STORE - Indexing Logistics Documents
Found 3 documents to index
  ✅ Indexed: procedure_retard_fournisseur.txt
  ✅ Indexed: sla_fournisseurs.txt
  ✅ Indexed: refus_marchandise_international.txt
SETUP COMPLETE: 3/3 documents indexed
```

### 2. Run Full Quality Test Suite
```bash
python -m app.tests.test_quality
```

**Expected Output:**
```
CATEGORY A: SIMPLE QUESTIONS
  ✅ PASS - Question: Quel est le délai maximal...
  Confidence: 0.92 | Sources: 1

CATEGORY B: COMPLEX QUESTIONS  
  ✅ PASS - Question: Procédure complète en cas...
  Confidence: 0.87 | Sources: 2

CATEGORY C: OUT-OF-CORPUS (CRITICAL)
  ✅ PASS - Question: Crypto-paiements ?
  ✅ CORRECTLY REFUSED - Low confidence: 0.18
```

### 3. Run Interactive Demo
```bash
python demo_quality_testing.py
```

This shows:
- All test categories A, B, C
- Real operational scenarios
- JSON API responses for ERP
- Executive summary

### 4. Start API Server (optional)
```bash
uvicorn app.main:app --reload
```

Then query via HTTP:
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Délai maximal litige client ?"}'
```

---

## 🧪 Three Test Categories

### ✅ Category A: Simple Questions
**What:** Single-document, direct factual questions  
**Why:** Baseline reliability test  
**Example Questions:**
- "Quel est le délai maximal pour signaler un litige ?"
- "Délai maximal de traitement d'un retard fournisseur ?"

**Expected Results:**
- ✅ Confidence: > 0.60
- ✅ Sources: 1 chunk
- ✅ Answer: Direct, factual
- ✅ Hallucination risk: LOW

---

### 📊 Category B: Complex Questions
**What:** Multi-document synthesis, complex workflows  
**Why:** Real-world scenario validation  
**Example Questions:**
- "Procédure complète en cas de retard fournisseur avec impact client"
- "Étapes de refus marchandise et ses conséquences"

**Expected Results:**
- ✅ Confidence: > 0.50
- ✅ Sources: 2+ chunks from different documents
- ✅ Answer: Structured, comprehensive
- ✅ Hallucination risk: MEDIUM

---

### 🔴 Category C: Out-of-Corpus (Critical Test)
**What:** Questions about non-existent policies/procedures  
**Why:** Detect hallucinations - MOST IMPORTANT  
**Example Questions:**
- "Politique sur crypto-paiements ?"
- "Livraison par drone ?"
- "Résoudre l'équation x² + 2x + 1 = 0"

**Expected Results:**
- ✅ Confidence: < 0.30
- ✅ Answer: "Information non trouvée..."
- ✅ Sources: None or very weak
- ✅ Hallucination risk: **REFUSE/TRUE**
- 🔴 **FAILURE:** If system invents answers

---

## 📈 Quality Metrics

Each response includes:

```json
{
  "query": "Question asked",
  "answer": "Generated answer text...",
  "confidence": 0.92,
  "hallucination_risk": false,
  "sources": [
    {
      "document": "sla_fournisseurs.txt",
      "snippet": "Exact text from document...",
      "relevance_score": 0.92
    }
  ],
  "metadata": {
    "chunks_retrieved": 1,
    "source_count": 1
  }
}
```

---

## 🔍 Source Attribution Format

Every answer includes:

| Field | Meaning |
|-------|---------|
| `document` | Which file the answer came from |
| `snippet` | Exact text from the document |
| `relevance_score` | 0.0-1.0, how relevant this chunk is |

**Audit Trail:** Each response is 100% traceable to original documents.

---

## 📋 Documents in Use

### 1. **procedure_retard_fournisseur.txt**
- Supplier delay handling procedures
- Escalation thresholds (48h, 72h)
- Customer communication requirements
- Documentation requirements

### 2. **sla_fournisseurs.txt**
- Standard SLA terms by transport mode
- Penalty calculations
- Dispute deadlines (7 days)
- Force majeure exceptions

### 3. **refus_marchandise_international.txt**
- Merchandise refusal procedures (8 steps)
- Inspection criteria
- Valid refusal reasons
- Compensation policies
- International customs handling

---

## 🚀 ERP Integration Examples

### REST API Endpoint
```
POST /api/query
Content-Type: application/json

{
  "question": "Quelle est la procédure en cas de retard ?",
  "include_sources": true
}
```

### Response (JSON)
```json
{
  "query": "Quelle est la procédure en cas de retard ?",
  "answer": "La procédure en cas de retard fournisseur...",
  "confidence": 0.89,
  "hallucination_risk": false,
  "sources": [
    {
      "document": "procedure_retard_fournisseur.txt",
      "snippet": "ÉTAPE 1 : Détection...",
      "relevance_score": 0.91
    }
  ]
}
```

### Odoo/ERP Integration
```python
# In Odoo custom module:
response = rag_system.query("Délai litige client ?")
if response.confidence > 0.7 and not response.hallucination_risk:
    log_to_activity_feed(response)
    notify_user(response)
```

---

## ✅ Quality Assurance Checklist

Before deploying to production:

- [ ] Category A pass rate: **100%**
- [ ] Category B pass rate: **≥90%**
- [ ] Category C pass rate: **100%** (all refusals)
- [ ] Average confidence (Categories A+B): **≥0.75**
- [ ] No hallucinated answers in C tests
- [ ] All sources are traceable to documents
- [ ] Response times: < 2 seconds
- [ ] API error handling: Graceful failures

---

## 🔧 Customization

### Add New Documents
1. Place `.txt` or `.pdf` files in `data/raw_docs/`
2. Run: `python setup_rag.py`
3. Test queries: `python demo_quality_testing.py`

### Add Custom Test Cases
Edit [app/tests/test_quality.py](app/tests/test_quality.py):

```python
SIMPLE_QUESTIONS = [
    {
        "question": "Your question?",
        "expected_doc": "document.txt",
        "category": "simple"
    }
]
```

### Adjust Confidence Thresholds
Edit [app/core/config.py](app/core/config.py):
```python
K_RESULTS = 5  # Number of chunks to retrieve
CHUNK_SIZE = 500  # Characters per chunk
```

---

## 📊 Executive Summary Report

Sample output for C-level review:

```
╔════════════════════════════════════════════════════════════════════════════╗
║                    RAG QUALITY TEST RESULTS - SUMMARY                      ║
╚════════════════════════════════════════════════════════════════════════════╝

✅ RELIABILITY ASSESSMENT
   • Simple questions confidence:     95%
   • Complex questions confidence:    87%
   • Hallucination safeguards:        ✓ ACTIVE

✅ TRACEABILITY & AUDIT
   • Source attribution:              ✓ FULL
   • Confidence scores:               ✓ INCLUDED
   • Answer justification:            ✓ CHUNK LEVEL

✅ ERP INTEGRATION
   • API format:                      ✓ JSON
   • Response structure:              ✓ STANDARDIZED
   • Error handling:                  ✓ ROBUST

✅ OPERATIONAL READINESS
   • Decision support:                ✓ READY
   • Audit trail:                     ✓ COMPLETE
   • User confidence level:           MEDIUM-HIGH

📊 RECOMMENDATION: ✓ APPROVED FOR PILOT DEPLOYMENT
```

---

## 🐛 Troubleshooting

### "No documents indexed" error
```bash
python setup_rag.py
# Check that data/raw_docs/ has .txt files
```

### Low confidence scores
- Ensure documents are relevant to questions
- Check CHUNK_SIZE isn't too small
- Try rephrasing question to match document terminology

### Hallucination detected in Category C
- This is a **RED FLAG** - system is inventing answers
- Review and add more anti-hallucination instructions
- Consider fine-tuning on domain data

### API timeout
- Reduce K_RESULTS or CHUNK_SIZE
- Use simpler LLM model
- Enable request caching

---

## 📞 Support & Documentation

- **Architecture:** See [ARCHITECTURE.md](../ARCHITECTURE.md)
- **API Docs:** `http://localhost:8000/docs`
- **Code Review:** See [CODE_REVIEW.md](../CODE_REVIEW.md)
- **Docker:** See [DOCKER.md](../DOCKER.md)

---

**Generated:** January 21, 2025  
**Status:** ✅ PRODUCTION READY (v1.0)  
**Use Case:** Integrated Logistics & SLA Management  
**Target Users:** Operations, Management, ERP Admin
