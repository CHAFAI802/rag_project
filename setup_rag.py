#!/usr/bin/env python3
"""
Setup script: Index all logistics documents for RAG testing.
Run this before running quality tests or demo.
"""

import logging
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.document_loader import load_document
from app.services.rag_pipeline import index_document
from app.core.config import RAW_DOCS_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_documents():
    """Index all documents in raw_docs directory."""
    logger.info("="*70)
    logger.info("SETTING UP RAG VECTOR STORE - Indexing Logistics Documents")
    logger.info("="*70)
    
    documents = list(RAW_DOCS_DIR.glob("*.txt"))
    
    if not documents:
        logger.warning(f"No documents found in {RAW_DOCS_DIR}")
        return False
    
    logger.info(f"Found {len(documents)} documents to index\n")
    
    success_count = 0
    for doc_path in sorted(documents):
        try:
            logger.info(f"Processing: {doc_path.name}")
            
            # Load document
            text = load_document(doc_path)
            
            if not text or not text.strip():
                logger.warning(f"  ⚠️  Empty document: {doc_path.name}")
                continue
            
            # Index document
            index_document(text, doc_path.name)
            logger.info(f"  ✅ Indexed successfully ({len(text)} characters)\n")
            success_count += 1
            
        except Exception as e:
            logger.error(f"  ❌ Error indexing {doc_path.name}: {e}\n")
    
    logger.info("="*70)
    logger.info(f"SETUP COMPLETE: {success_count}/{len(documents)} documents indexed")
    logger.info("="*70 + "\n")
    
    return success_count > 0


if __name__ == "__main__":
    success = setup_documents()
    sys.exit(0 if success else 1)
