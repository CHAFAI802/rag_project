import logging
import numpy as np
from app.core.embeddings import embed_texts, embed_query
from app.core.vectorstore import VectorStore
from app.services.chunker import chunk_text
from app.core.llm import generate_answer
from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP, K_RESULTS, EMBEDDING_DIM

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
    try:
        logger.info(f"Processing query: {question[:50]}...")
        
        query_vec = embed_query(question)
        logger.debug(f"Query embedding shape: {query_vec.shape}")
        
        # Use actual dimension from embedding
        dim = len(query_vec) if isinstance(query_vec, list) else query_vec.shape[0]
        store = VectorStore(dim)
        
        if store.index.ntotal == 0:
            logger.warning("FAISS index is empty")
            return "No documents indexed. Please ingest documents first."
        
        distances, indices = store.search(query_vec, k=K_RESULTS)
        
        if len(indices) == 0:
            logger.warning("No relevant documents found")
            return "No relevant information found."
        
        retrieved = [store.metadata[i]["text"] for i in indices]
        context = "\n".join(retrieved)
        
        logger.debug(f"Retrieved {len(retrieved)} chunks")
        
        answer = generate_answer(context, question)
        logger.info(f"Generated answer (length: {len(answer)} chars)")
        
        return answer
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise
