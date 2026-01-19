from fastapi import FastAPI
from app.api.ingest import router as ingest_router 
from app.api.query import router as query_router




app = FastAPI(title="RAG Document Search API")

app.include_router(ingest_router, prefix="/api", tags=["Ingest"])
app.include_router(query_router, prefix="/api", tags=["Query"])


@app.get("/health")
def health_check():
    return {"status": "healthy"}
