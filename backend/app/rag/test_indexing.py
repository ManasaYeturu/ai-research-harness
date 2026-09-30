from backend.app.rag.indexer import index_document
from backend.app.rag.vector_store import (
    client,
    COLLECTION_NAME,
)


FILE_PATH = "knowledge/documents/postgres.md"


def test_document_indexing():
    result = index_document(
        file_path=FILE_PATH,
        chunk_size=300,
    )

    collection_info = client.get_collection(
        collection_name=COLLECTION_NAME,
    )

    assert (
        result["stored_count"]
        == result["chunk_count"]
    )

    assert result["stored_count"] > 0

    assert (
        collection_info.points_count
        >= result["stored_count"]
    )