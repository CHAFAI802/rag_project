import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag_pipeline import query_rag

logger = logging.getLogger(__name__)
router = APIRouter()


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="Question to ask")


@router.post("/query")
async def query_documents(data: QueryRequest):
    """
    Query the indexed documents and get an answer.
    """
    try:
        logger.info(f"Processing query: {data.question[:50]}...")
        answer = query_rag(data.question)
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error processing query"
        )
