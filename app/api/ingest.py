import logging
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path

from app.services.document_loader import load_document
from app.services.rag_pipeline import index_document
from app.core.config import RAW_DOCS_DIR

logger = logging.getLogger(__name__)

router = APIRouter()

# Max file size: 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024


@router.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """
    Ingest a document by uploading, extracting text, and indexing.
    
    Supports: .pdf, .docx, .txt, .md
    """
    try:
        # Validate file
        if not file.filename:
            logger.error("Empty filename")
            raise HTTPException(status_code=400, detail="Filename required")
        
        # Check file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            logger.error(f"File too large: {file_size} bytes")
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Max size: {MAX_FILE_SIZE / (1024*1024):.0f}MB"
            )
        
        if file_size == 0:
            logger.error("Empty file uploaded")
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Save file
        RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
        file_path = RAW_DOCS_DIR / file.filename
        
        logger.info(f"Saving file: {file_path}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text
        logger.info(f"Extracting text from: {file.filename}")
        text = load_document(file_path)
        
        if not text or not text.strip():
            logger.warning(f"Empty document after extraction: {file.filename}")
            raise HTTPException(
                status_code=400, 
                detail="No text extracted from document"
            )
        
        # Index document
        logger.info(f"Indexing document: {file.filename}")
        index_document(text, file.filename)
        
        logger.info(f"Successfully ingested: {file.filename}")
        
        return {
            "filename": file.filename,
            "chars_extracted": len(text),
            "file_size_bytes": file_size,
            "status": "indexed"
        }
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Invalid file format: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid format: {str(e)}")
    except Exception as e:
        logger.error(f"Error ingesting document: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="Internal server error during ingestion"
        )