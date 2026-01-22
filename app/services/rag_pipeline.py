import logging
import numpy as np
from typing import Tuple, List, Dict
from app.core.embeddings import embed_texts, embed_query
from app.core.vectorstore import VectorStore
from app.services.chunker import chunk_text
from app.core.llm import generate_answer
from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP, K_RESULTS, EMBEDDING_DIM
from app.models.response_models import QueryResponse, SourceChunk

logger = logging.getLogger(__name__)


def index_document(text: str, source: str):
    """
    Index a document by chunking, embedding, and storing in FAISS.
    
    Args:
        text: Document text to index
        source: Source identifier (e.g., filename)
    """
    try:
        logger.info(f"Starting indexing for source: {source}")
        
        chunks = chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        logger.debug(f"Created {len(chunks)} chunks")
        
        if not chunks:
            logger.warning(f"No chunks created for {source}")
            return
        
        embeddings = embed_texts(chunks)
        
        if not isinstance(embeddings, np.ndarray):
            embeddings = np.array(embeddings, dtype="float32")
        else:
            embeddings = embeddings.astype("float32")
        
        logger.debug(f"Embedding shape: {embeddings.shape}")
        
        dim = embeddings.shape[1]
        store = VectorStore(dim)
        
        metadatas = [{"text": c, "source": source} for c in chunks]
        store.add(embeddings, metadatas)
        
        logger.info(f"Successfully indexed {source} with {len(chunks)} chunks")
    except Exception as e:
        logger.error(f"Error indexing document {source}: {e}")
        raise


def query_rag(question: str) -> str:
    """
    Query the RAG system and generate an answer.
    
    Args:
        question: User question
        
    Returns:
        Generated answer based on retrieved context
    """
    response = query_rag_with_sources(question)
    return response.answer


def query_rag_with_sources(question: str) -> QueryResponse:
    """
    Query the RAG system and return answer with full source tracking.
    
    Args:
        question: User question
        
    Returns:
        QueryResponse with answer, sources, and confidence scores
    """
    try:
        logger.info(f"Processing query: {question[:50]}...")
        
        query_vec = embed_query(question)
        logger.debug(f"Query embedding shape: {query_vec.shape}")
        
        # Use actual dimension from embedding
        dim = len(query_vec) if isinstance(query_vec, list) else query_vec.shape[0]
        store = VectorStore(dim)
        
        if store.index.ntotal == 0:
            logger.warning("FAISS index is empty")
            return QueryResponse(
                query=question,
                answer="No documents indexed. Please ingest documents first.",
                sources=[],
                confidence=0.0,
                num_chunks_retrieved=0,
                is_hallucination_risk=True
            )
        
        distances, indices = store.search(query_vec, k=K_RESULTS)
        
        if len(indices) == 0:
            logger.warning("No relevant documents found")
            return QueryResponse(
                query=question,
                answer="No relevant information found.",
                sources=[],
                confidence=0.0,
                num_chunks_retrieved=0,
                is_hallucination_risk=True
            )
        
        # Build sources with scores (convert distances to similarity scores)
        sources: List[SourceChunk] = []
        retrieved_texts = []
        
        for i, idx in enumerate(indices):
            # Convert distance to similarity score (0-1)
            # FAISS returns L2 distance; convert to cosine-like score
            distance = distances[i]  # distances is already a flat list from VectorStore.search()
            similarity_score = max(0.0, 1.0 - (distance / 2.0))  # Normalize L2 distance
            
            metadata = store.metadata[idx]
            chunk_text = metadata.get("text", "")
            source_doc = metadata.get("source", "unknown")
            
            sources.append(SourceChunk(
                document=source_doc,
                chunk=chunk_text,
                score=float(similarity_score),
                chunk_index=i
            ))
            retrieved_texts.append(chunk_text)
        
        # Build structured context with headers for better LLM understanding
        context_parts = []
        for i, text in enumerate(retrieved_texts, 1):
            context_parts.append(f"[Source {i}] {text}")
        
        context = "\n\n".join(context_parts)
        logger.debug(f"Retrieved {len(retrieved_texts)} chunks, context length: {len(context)}")
        
        # Generate answer
        answer = generate_answer(context, question)
        logger.info(f"Generated answer (length: {len(answer)} chars)")
        
        # Calculate confidence as average similarity score
        avg_confidence = np.mean([s.score for s in sources]) if sources else 0.0
        
        # Detect hallucination risk: if confidence is low or answer doesn't match sources
        is_hallucination_risk = avg_confidence < 0.5
        
        response = QueryResponse(
            query=question,
            answer=answer,
            sources=sources,
            confidence=float(avg_confidence),
            num_chunks_retrieved=len(retrieved_texts),
            is_hallucination_risk=is_hallucination_risk
        )
        
        logger.info(f"Response confidence: {avg_confidence:.3f}, hallucination risk: {is_hallucination_risk}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise
