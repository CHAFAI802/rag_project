from app.core.embeddings import embed_texts, embed_query
from app.core.vectorstore import VectorStore
from app.services.chunker import chunk_text
from app.core.llm import generate_answer


def index_document(text: str, source: str):
    chunks = chunk_text(text)

    embeddings = embed_texts(chunks)
    dim = embeddings.shape[1]

    store = VectorStore(dim)

    metadatas = [{"text": c, "source": source} for c in chunks]

    store.add(embeddings, metadatas)


def query_rag(question: str) -> str:
    query_vec = embed_query(question)

    store = VectorStore(len(query_vec))

    distances, indices = store.search(query_vec)

    if len(indices) == 0:
        return "No relevant information found."

    retrieved = [store.metadata[i]["text"] for i in indices]

    context = "\n".join(retrieved)

    return generate_answer(context, question)
