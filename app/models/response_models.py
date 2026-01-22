"""
Data models for RAG system responses with source tracking.
Enables transparent, traceable answers grounded in documents.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SourceChunk(BaseModel):
    """A source chunk represents a piece of retrieved context."""
    
    document: str = Field(..., description="Document filename or identifier")
    chunk: str = Field(..., description="Actual text from the document")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")
    chunk_index: Optional[int] = Field(None, description="Chunk index in document")


class QueryResponse(BaseModel):
    """Response to a query with full source tracking."""
    
    query: str = Field(..., description="Original user query")
    answer: str = Field(..., description="Generated answer based on retrieved context")
    sources: List[SourceChunk] = Field(default_factory=list, description="List of source chunks used")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Average confidence score")
    num_chunks_retrieved: int = Field(..., ge=0, description="Number of chunks retrieved")
    is_hallucination_risk: bool = Field(default=False, description="True if answer might be hallucinated")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response generation time")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Délai maximal de traitement d'un litige client ?",
                "answer": "Le délai maximal pour signaler un litige est de 7 jours après livraison...",
                "sources": [
                    {
                        "document": "sla_fournisseurs.txt",
                        "chunk": "Délai maximal pour signaler un litige : 7 jours après livraison",
                        "score": 0.92,
                        "chunk_index": 3
                    }
                ],
                "confidence": 0.92,
                "num_chunks_retrieved": 1,
                "is_hallucination_risk": False,
                "timestamp": "2025-01-21T14:30:00"
            }
        }


class BulkQueryResponse(BaseModel):
    """Response for bulk query operations."""
    
    total_queries: int = Field(..., description="Total number of queries processed")
    successful: int = Field(..., description="Number of successful queries")
    failed: int = Field(..., description="Number of failed queries")
    avg_confidence: float = Field(..., ge=0.0, le=1.0, description="Average confidence across queries")
    results: List[QueryResponse] = Field(default_factory=list, description="Individual query results")


class QualityMetrics(BaseModel):
    """Quality metrics for testing."""
    
    test_category: str = Field(..., description="Category: simple|complex|out_of_corpus")
    question: str = Field(..., description="Test question")
    answer: str = Field(..., description="RAG answer")
    expected_behavior: str = Field(..., description="Expected behavior")
    passed: bool = Field(..., description="Whether test passed")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in answer")
    has_sources: bool = Field(..., description="Whether answer has source citations")
    num_sources: int = Field(..., description="Number of sources cited")
    is_coherent: bool = Field(..., description="Whether answer is coherent and on-topic")
    is_hallucinated: bool = Field(..., description="Whether hallucinations detected")


class QualityTestReport(BaseModel):
    """Complete quality test report."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_tests: int = Field(..., description="Total tests run")
    passed_tests: int = Field(..., description="Tests passed")
    test_metrics: List[QualityMetrics] = Field(default_factory=list)
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100
    
    @property
    def avg_confidence(self) -> float:
        """Calculate average confidence."""
        if not self.test_metrics:
            return 0.0
        return sum(m.confidence_score for m in self.test_metrics) / len(self.test_metrics)
