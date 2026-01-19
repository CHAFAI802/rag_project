from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_pipeline import query_rag

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


@router.post("/query")
def query_documents(data: QueryRequest):
    answer = query_rag(data.question)
    return {"answer": answer}
