from backend.app.rag.loader import load_document
from backend.app.rag.chunker import chunk_text
from backend.app.rag.embeddings import generate_embeddings
from backend.app.rag.vector_store import (
    create_collection,
    store_chunks
)


def index_document(
    file_path: str,
    chunk_size: int = 300
):
    """
    Load a document, split it into chunks,
    generate embeddings, and store the chunks
    in Qdrant.
    """

    # 1. Load document
    document = load_document(file_path)

    # 2. Chunk document
    chunks = chunk_text(
        document["content"],
        chunk_size=chunk_size
    )

    if not chunks:
        raise ValueError(
            "Document produced no chunks."
        )

    # 3. Generate embeddings
    vectors = generate_embeddings(chunks)

    # 4. Create Qdrant collection
    create_collection()

    # 5. Store chunks and vectors
    stored_count = store_chunks(
        chunks=chunks,
        vectors=vectors,
        source=document["metadata"]["source"]
    )

    return {
        "source": document["metadata"]["source"],
        "chunk_count": len(chunks),
        "vector_count": len(vectors),
        "stored_count": stored_count
    }