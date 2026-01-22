import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag_pipeline import query_rag, query_rag_with_sources
from app.models.response_models import QueryResponse

logger = logging.getLogger(__name__)
router = APIRouter()


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="Question to ask")
    include_sources: bool = Field(default=True, description="Include source documents in response")


@router.post("/query")
async def query_documents(data: QueryRequest) -> QueryResponse:
    """
    Query the indexed documents and get an answer with sources.
    
    Returns a structured response with:
    - answer: Generated answer based on retrieved documents
    - sources: List of source chunks with relevance scores
    - confidence: Average confidence score
    - is_hallucination_risk: Flag indicating hallucination risk
    """
    try:
        logger.info(f"Processing query: {data.question[:50]}...")
        
        # Get response with sources
        response = query_rag_with_sources(data.question)
        
        logger.info(f"Query processed successfully. Confidence: {response.confidence:.3f}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@router.post("/query-simple")
async def query_simple(data: QueryRequest) -> dict:
    """
    Simple endpoint that returns just the answer string.
    Backward compatible with basic clients.
    """
    try:
        logger.info(f"Processing simple query: {data.question[:50]}...")
        answer = query_rag(data.question)
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error processing query"
        )
