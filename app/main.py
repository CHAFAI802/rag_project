import logging
from fastapi import FastAPI
from app.api.ingest import router as ingest_router 
from app.api.query import router as query_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Document Search API")

app.include_router(ingest_router, prefix="/api", tags=["Ingest"])
app.include_router(query_router, prefix="/api", tags=["Query"])


@app.get("/health")
def health_check():
    logger.debug("Health check called")
    return {"status": "healthy"}
