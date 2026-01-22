def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """Chunk text with overlap, filtering empty chunks."""
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    
    if not text or not text.strip():
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()
        # Only add non-empty chunks
        if chunk and len(chunk) > 50:  # Minimum chunk size for meaningful content
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def chunk_documents(docs: list[str], chunk_size=500, overlap=100) -> list[str]:
    all_chunks = []
    for doc in docs:
        chunks = chunk_text(doc, chunk_size, overlap)
        all_chunks.extend(chunks)
    return all_chunks
