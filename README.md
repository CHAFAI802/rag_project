# 🚀 RAG Document Search API

> **Retrieval-Augmented Generation API** - Semantic search over documents using embeddings + LLM

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com/)
[![FAISS](https://img.shields.io/badge/FAISS-CPU-yellow)](https://faiss.ai/)
[![Tests](https://img.shields.io/badge/tests-11%2F11%20PASS-brightgreen)](#-testing)

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## 📖 Overview

RAG Document Search API enables **semantic search and question-answering** over your documents:

1. **Upload documents** (PDF, DOCX, TXT, MD)
2. **Automatic extraction** & chunking
3. **Semantic embedding** via HuggingFace
4. **FAISS indexing** for fast retrieval
5. **LLM-powered answers** from context

### Why RAG?

- 🎯 **Accurate answers** grounded in your documents
- 🚀 **Fast retrieval** using vector similarity search
- 💰 **Cost-effective** with lightweight models (distilgpt2)
- 🔒 **Private** - runs locally or on your infrastructure

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
├──────────────┬──────────────┬──────────────────────────────┤
│   /api/ingest   │   /api/query   │   /health               │
└──────┬───────┴───────┬───────┴──────────────────────────────┘
       │               │
       ▼               ▼
┌────────────┐   ┌──────────────┐
│ Document   │   │ Embeddings   │
│ Loader     │   │ (HF API)     │
├────────────┤   ├──────────────┤
│ PDF, DOCX, │   │ all-MiniLM   │
│ TXT, MD    │   │ (384 dims)   │
└────────────┘   └──────────────┘
       │               │
       └───┬───────────┘
           ▼
    ┌──────────────┐
    │  Chunker     │
    ├──────────────┤
    │ 500 chars    │
    │ 100 overlap  │
    └──────┬───────┘
           ▼
    ┌──────────────┐
    │ FAISS Index  │
    ├──────────────┤
    │ Vector Store │
    │ + Metadata   │
    └──────┬───────┘
           │
    ┌──────▼──────────┐
    │ LLM Generation  │
    ├─────────────────┤
    │ distilgpt2 (CPU)│
    │ 350MB RAM       │
    └─────────────────┘
```

### Data Flow

**Ingestion Pipeline:**
```
Document Upload → Extract Text → Chunk (500c, 100ov) → Embed → FAISS Index
```

**Query Pipeline:**
```
Question → Embed → FAISS Search (k=5) → Retrieve Context → LLM Answer
```

---

## ⚡ Quick Start

### 1. Clone & Setup (5 min)

```bash
# Clone repository
git clone https://github.com/CHAFAI802/rag_project.git
cd rag_project

# Create virtual environment
python3.10 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your HuggingFace token
```

### 2. Get HuggingFace Token (2 min)

1. Go to https://huggingface.co/settings/tokens
2. Create new token (read access)
3. Copy token to `.env`:

```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx
```

### 3. Run Server (1 min)

```bash
uvicorn app.main:app --reload
```

Server runs at: **http://localhost:8000**

### 4. Test It (2 min)

**Upload a document:**
```bash
curl -X POST http://localhost:8000/api/ingest \
  -F "file=@path/to/document.pdf"
```

**Ask a question:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?"}'
```

**View API docs:**
Open http://localhost:8000/docs in your browser

---

## 📦 Installation

### Requirements

- **Python 3.10+**
- **8GB RAM** (minimum, 16GB recommended)
- **2GB disk space** for models + indices
- **HuggingFace API token** (free)

### Step-by-Step

```bash
# 1. Clone repo
git clone https://github.com/CHAFAI802/rag_project.git
cd rag_project

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env and add your HF_TOKEN

# 5. Verify installation
python -c "from app.core.embeddings import embed_query; print('✅ Installation OK')"

# 6. Run tests
python test_api.py
python test_integration.py

# 7. Start server
uvicorn app.main:app --reload
```

### Using Docker (Optional)

```bash
# Build image
docker build -t rag-api .

# Run container
docker run -p 8000:8000 \
  -e HF_TOKEN=your_token \
  -v $(pwd)/data:/app/data \
  rag-api

# Or use docker-compose
docker-compose up
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file (copy from `.env.example`):

```env
# Required: HuggingFace API token
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx

# Optional: Chunking parameters
CHUNK_SIZE=500              # Characters per chunk
CHUNK_OVERLAP=100           # Overlap between chunks

# Optional: Embedding model
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
VECTOR_DIMENSION=384        # Output dimension of embedding model
```

### File Structure

```
rag_project/
├── app/
│   ├── main.py             # FastAPI app
│   ├── api/
│   │   ├── ingest.py       # Document upload endpoint
│   │   └── query.py        # Query endpoint
│   ├── core/
│   │   ├── config.py       # Configuration
│   │   ├── embeddings.py   # HF embeddings
│   │   ├── llm.py          # LLM inference
│   │   └── vectorstore.py  # FAISS wrapper
│   └── services/
│       ├── chunker.py      # Text chunking
│       ├── document_loader.py  # File parsing
│       └── rag_pipeline.py # RAG orchestration
├── data/
│   ├── raw_docs/           # Uploaded documents
│   └── faiss_index/        # FAISS indices
├── tests/
│   ├── test_api.py         # API tests
│   └── test_integration.py # Integration tests
└── requirements.txt        # Dependencies
```

---

## 🎯 Usage

### Python API

```python
from app.services.rag_pipeline import index_document, query_rag

# Index a document
with open("document.txt") as f:
    text = f.read()
index_document(text, source="document.txt")

# Query
answer = query_rag("What is the main topic?")
print(answer)
```

### FastAPI Endpoints

#### Health Check

```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

#### Ingest Document

```bash
POST /api/ingest
```

**Parameters:**
- `file` (required): Document file (PDF, DOCX, TXT, MD)

**Request:**
```bash
curl -X POST http://localhost:8000/api/ingest \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "filename": "document.pdf",
  "chars_extracted": 15234,
  "file_size_bytes": 102340,
  "status": "indexed"
}
```

**Errors:**
- `400`: File too large (>50MB) or empty
- `400`: Unsupported format
- `500`: Processing error

#### Query Documents

```bash
POST /api/query
```

**Body:**
```json
{
  "question": "Your question here"
}
```

**Request:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Python?"}'
```

**Response:**
```json
{
  "answer": "Python is a high-level programming language..."
}
```

**Constraints:**
- Question: 1-1000 characters
- Returns: Best answer from indexed documents

**Errors:**
- `400`: Empty question
- `422`: Invalid input format
- `500`: Processing error

---

## 📚 API Documentation

### Interactive API Docs

**Swagger UI:** http://localhost:8000/docs

**ReDoc:** http://localhost:8000/redoc

Both provide interactive API testing and detailed documentation.

### Request/Response Examples

**Example 1: Ingest Python Tutorial**

```bash
# Upload file
curl -X POST http://localhost:8000/api/ingest \
  -F "file=@python_tutorial.pdf"

# Response
{
  "filename": "python_tutorial.pdf",
  "chars_extracted": 25670,
  "file_size_bytes": 340120,
  "status": "indexed"
}
```

**Example 2: Query About Python**

```bash
# Ask question
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How do you create a function in Python?"}'

# Response
{
  "answer": "To create a function in Python, use the def keyword followed by the function name and parentheses containing any parameters. For example: def my_function(param1, param2): body of function"
}
```

**Example 3: Multiple Documents**

```bash
# Ingest multiple docs
for doc in *.pdf; do
  curl -X POST http://localhost:8000/api/ingest \
    -F "file=@$doc"
done

# Query searches all indexed documents
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Find information about X"}'
```

---

## 🧪 Testing

### Run All Tests

```bash
# Integration tests (chunking, vectorstore, RAG pipeline)
python test_integration.py

# API endpoint tests
python test_api.py

# Embedding tests
python test_hf_api.py
```

### Expected Output

```
✅ Chunking: PASS
✅ VectorStore: PASS
✅ Full Pipeline: PASS
✅ Health: PASS
✅ Ingest: PASS
✅ Query: PASS
✅ Validation: PASS

🎉 ALL TESTS PASSED!
```

### Test Coverage

| Component | Tests |
|-----------|-------|
| Embeddings | embed_texts, embed_query |
| Chunking | chunk_text, overlaps |
| VectorStore | add, search, persistence |
| RAG Pipeline | indexing, querying |
| API Endpoints | health, ingest, query |
| Validation | input constraints, error handling |

---

## 🛠️ Development

### Project Structure

```
.
├── app/                  # Application code
│   ├── api/             # FastAPI routes
│   ├── core/            # Business logic
│   ├── services/        # Data processing
│   └── main.py          # App entry point
├── data/                # Data storage (git-ignored)
├── tests/               # Test files
├── .github/             # GitHub configurations
├── requirements.txt     # Dependencies
├── .env.example         # Environment template
└── README.md           # This file
```

### Adding New Features

1. **New Endpoint:**
   ```python
   # app/api/new_endpoint.py
   from fastapi import APIRouter
   
   router = APIRouter()
   
   @router.post("/new-action")
   async def new_action():
       ...
   
   # app/main.py
   from app.api.new_endpoint import router as new_router
   app.include_router(new_router, prefix="/api")
   ```

2. **New Service:**
   ```python
   # app/services/new_service.py
   def process_data(input_data):
       # Implementation
       return result
   ```

3. **Add Tests:**
   ```python
   # test_new_feature.py
   def test_new_feature():
       assert new_feature() == expected_result
       print("✅ Test passed")
   ```

### Code Quality

```bash
# Type checking
pip install mypy
mypy app/

# Linting
pip install pylint
pylint app/

# Formatting
pip install black
black app/
```

---

## 🐛 Troubleshooting

### Issue: "HF_TOKEN manquant"

**Solution:**
```bash
# 1. Create .env file
cp .env.example .env

# 2. Add your token
echo "HF_TOKEN=your_token_here" >> .env

# 3. Verify
source .venv/bin/activate
python -c "from app.core.config import HF_TOKEN; print(HF_TOKEN)"
```

### Issue: "Out of Memory"

**Solution:**
- The app uses **distilgpt2** (~350MB)
- Requires **~4GB total RAM**
- If OOM errors: reduce chunk_size or use smaller model

```bash
# Check memory usage
free -h  # Linux
# or
top  # Linux/Mac
# or
tasklist  # Windows
```

### Issue: "FAISS index not found"

**Solution:**
```bash
# Index is created on first ingest
# Ensure data/faiss_index/ exists:
mkdir -p data/faiss_index

# Try ingesting a document again:
curl -X POST http://localhost:8000/api/ingest \
  -F "file=@test.txt"
```

### Issue: "No relevant information found"

**Solution:**
- Upload more documents with relevant content
- Ask more specific questions
- Check document was indexed:

```bash
# View metadata
cat data/faiss_index/metadata.json | python -m json.tool
```

### Issue: Slow response time

**Solutions:**
1. **First query slow** = LLM loading (first time ~30s)
   - Subsequent queries are fast
   
2. **Consistent slowness** = Check:
   - CPU usage: `top` or Task Manager
   - Disk I/O: `iotop` (Linux)
   - Network: Check HF API rate limits

3. **Optimization:**
   ```python
   # Reduce k results
   K_RESULTS = 3  # Default 5
   
   # Reduce LLM tokens
   LLM_MAX_TOKENS = 100  # Default 300
   ```

### Issue: "Connection refused" on port 8000

**Solution:**
```bash
# Check port availability
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Use different port
uvicorn app.main:app --port 8001
```

---

## 📝 Contributing

We welcome contributions! Please:

1. **Fork** the repository
2. **Create branch**: `git checkout -b feature/my-feature`
3. **Make changes** and test: `python test_*.py`
4. **Commit**: `git commit -m "Add my feature"`
5. **Push**: `git push origin feature/my-feature`
6. **Open PR** with description

### Development Guidelines

- Follow PEP 8 style guide
- Add type hints to functions
- Write tests for new features
- Update documentation
- Keep commits atomic and descriptive

---

## 📊 Performance

### Benchmarks (on 4GB RAM machine)

| Operation | Time | Notes |
|-----------|------|-------|
| Upload PDF (5MB) | 2-5s | Extraction + chunking |
| Index 100 chunks | 1-2s | Embedding + FAISS |
| Search query | <1s | FAISS similarity search |
| LLM generation | 10-30s | First run loads model |
| LLM generation | 5-15s | Cached model |

### Scaling Tips

- **Multiple documents:** FAISS scales well up to millions of vectors
- **Concurrent requests:** Use multi-worker uvicorn
- **High throughput:** Add Redis caching layer
- **Production:** Deploy with Docker + load balancer

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🙋 Support

- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions
- **Email:** support@example.com

---

## 🔗 Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [HuggingFace Inference API](https://huggingface.co/inference-api)
- [FAISS Documentation](https://faiss.ai/)
- [Sentence Transformers](https://www.sbert.net/)

---

**Made with ❤️ by CHAFAI MABROUK**

Last updated: January 19, 2026
