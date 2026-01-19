# Copilot Instructions for RAG Document Search API

## Project Overview
This is a **Retrieval-Augmented Generation (RAG) API** built with FastAPI that enables semantic search over ingested documents. The system embeds documents, stores them in FAISS vector indices, and retrieves relevant context to generate LLM answers.

## Core Architecture

### Component Layout
- **`app/api/`**: FastAPI endpoints for `/api/ingest` and `/api/query`
- **`app/core/`**: Infrastructure modules (embeddings, vectorstore, LLM)
- **`app/services/`**: Business logic (document loading, chunking, RAG pipeline)
- **`data/`**: Persistent storage for raw docs and FAISS indices

### Data Flow

**Ingestion Pipeline** → `POST /api/ingest`:
1. Document uploaded → saved to `data/raw_docs/`
2. `document_loader.py` extracts text (supports `.pdf`, `.docx`, `.txt`, `.md`)
3. `chunker.py` splits text into overlapping chunks (default: 500 chars, 100 overlap)
4. `embeddings.py` vectorizes chunks using `sentence-transformers/all-MiniLM-L6-v2` via HuggingFace Inference API
5. `VectorStore` adds vectors to FAISS index, saves to `data/faiss_index/`

**Query Pipeline** → `POST /api/query`:
1. Question embedded using same model
2. FAISS search retrieves top-k similar chunks (k=5)
3. Retrieved text concatenated as context
4. Context + question sent to `mistralai/Mistral-7B-Instruct-v0.2` for generation
5. LLM returns answer restricted to provided context

### Key Integration Points
- **HuggingFace API**: Required `HF_TOKEN` env var for embeddings (`embeddings.py` line 8)
- **FAISS**: CPU-based vector search, persisted as index + JSON metadata
- **Transformers**: Local LLM pipeline (lazy-loaded singleton in `llm.py`)
- **Pydantic**: Request validation (`QueryRequest` model)

## Critical Patterns & Conventions

### VectorStore Initialization
Always instantiate with embedding dimension: `VectorStore(dim)`. Automatically loads existing index if present:
```python
store = VectorStore(embeddings.shape[1])  # Use vector dimensionality
```

### Chunking Strategy
- Default: 500-char chunks with 100-char overlap (preserves context across boundaries)
- `overlap` must be < `chunk_size`, raises `ValueError` otherwise
- Used in both `rag_pipeline.index_document()` and standalone `chunker.chunk_documents()`

### Metadata Association
Chunk metadata stored as `{"text": chunk_content, "source": filename}` in JSON alongside FAISS index. Index consistency depends on maintaining aligned ordering.

### LLM Singleton Pattern
`llm.py` uses global singleton to avoid reloading the 7B model:
```python
_llm = None  # Cached after first call

def get_llm():
    global _llm
    if _llm is None:
        _llm = pipeline(...)
    return _llm
```

## Developer Workflows

### Setup
```bash
# Requires Python 3.10+, HF_TOKEN env var
pip install -r requirements.txt
```

### Running the Server
```bash
uvicorn app.main:app --reload
```
- Health check: `GET /health`
- Swagger UI: `http://localhost:8000/docs`

### Testing
Document ingestion workflow manually:
```bash
curl -X POST http://localhost:8000/api/ingest \
  -F "file=@data/raw_docs/document1.txt"

curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Your question here"}'
```

### Common Debugging
- **Missing embeddings**: Check `HF_TOKEN` env var, network connectivity to HuggingFace
- **FAISS dimension mismatch**: Ensure chunk vectors match query vector dimensions (both from same model)
- **Empty search results**: Verify metadata indices align with FAISS index size (check `vectorstore.py` line 24-25)
- **LLM memory issues**: Mistral-7B requires ~16GB RAM; cpu-only mode in `torch` config

## File Reference
- [app/services/rag_pipeline.py](app/services/rag_pipeline.py) — Core orchestration logic
- [app/core/vectorstore.py](app/core/vectorstore.py) — FAISS persistence & search
- [app/api/ingest.py](app/api/ingest.py) — Document upload endpoint
- [app/services/document_loader.py](app/services/document_loader.py) — Format parsing (PDF, DOCX, TXT)
