from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)


QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

COLLECTION_NAME = "knowledge_base"
VECTOR_SIZE = 768


client = QdrantClient(
    host=QDRANT_HOST,
    port=QDRANT_PORT,
)


def create_collection():
    """
    Create the knowledge base collection if it
    does not already exist.
    """

    collections = client.get_collections()

    collection_names = [
        collection.name
        for collection in collections.collections
    ]

    if COLLECTION_NAME not in collection_names:

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

        print(
            f"Collection '{COLLECTION_NAME}' created."
        )

    else:

        print(
            f"Collection '{COLLECTION_NAME}' already exists."
        )


def collection_exists():
    """
    Check whether the knowledge base collection exists.
    """

    collections = client.get_collections()

    return any(
        collection.name == COLLECTION_NAME
        for collection in collections.collections
    )


def store_chunks(
    chunks: list[str],
    vectors: list[list[float]],
    source: str,
):
    """
    Store document chunks and their embeddings
    in Qdrant.

    Each chunk receives a globally unique Qdrant
    point ID so chunks from different documents
    cannot overwrite each other.
    """

    if len(chunks) != len(vectors):
        raise ValueError(
            "Number of chunks must match number of vectors."
        )

    if not source or not source.strip():
        raise ValueError(
            "Source cannot be empty."
        )

    if not chunks:
        return 0

    points = []

    for chunk_id, (chunk, vector) in enumerate(
        zip(chunks, vectors)
    ):
        point = PointStruct(
            id=str(uuid4()),
            vector=vector,
            payload={
                "source": source,
                "chunk_id": chunk_id,
                "text": chunk,
            },
        )

        points.append(point)

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    return len(points)