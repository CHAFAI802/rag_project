def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def chunk_documents(docs: list[str], chunk_size=500, overlap=100) -> list[str]:
    all_chunks = []
    for doc in docs:
        chunks = chunk_text(doc, chunk_size, overlap)
        all_chunks.extend(chunks)
    return all_chunks
