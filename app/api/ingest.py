from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import shutil

from app.services.document_loader import load_document
from app.services.rag_pipeline import index_document

router = APIRouter()

DATA_DIR = Path("data/raw_docs")
DATA_DIR.mkdir(parents=True, exist_ok=True)



@router.post("/ingest")
def ingest_document(file: UploadFile = File(...)):
    file_path = DATA_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = load_document(file_path)
    index_document(text, file.filename)

    return {
        "filename": file.filename,
        "chars_extracted": len(text),
        "status": "indexed"
    }