import pytest

from backend.app.rag import vector_store


def test_collection_name_is_correct():
    assert vector_store.COLLECTION_NAME == "knowledge_base"


def test_vector_size_is_correct():
    assert vector_store.VECTOR_SIZE == 768


def test_collection_exists_returns_boolean():
    result = vector_store.collection_exists()

    assert isinstance(result, bool)


def test_create_collection_does_not_fail():
    vector_store.create_collection()

    assert vector_store.collection_exists()


def test_store_chunks_rejects_mismatched_lengths(
    monkeypatch,
):
    chunks = [
        "First chunk",
        "Second chunk",
    ]

    vectors = [
        [0.1, 0.2, 0.3],
    ]

    with pytest.raises(ValueError):
        vector_store.store_chunks(
            chunks=chunks,
            vectors=vectors,
            source="test.md",
        )


def test_store_chunks_rejects_empty_source():
    with pytest.raises(ValueError):
        vector_store.store_chunks(
            chunks=["Test chunk"],
            vectors=[[0.1, 0.2, 0.3]],
            source="",
        )


def test_store_chunks_returns_zero_for_empty_chunks(
    monkeypatch,
):
    result = vector_store.store_chunks(
        chunks=[],
        vectors=[],
        source="test.md",
    )

    assert result == 0


def test_store_chunks_creates_points_with_unique_ids(
    monkeypatch,
):
    captured_points = []

    def fake_upsert(
        collection_name,
        points,
    ):
        captured_points.extend(points)

    monkeypatch.setattr(
        vector_store.client,
        "upsert",
        fake_upsert,
    )

    chunks = [
        "First chunk",
        "Second chunk",
        "Third chunk",
    ]

    vectors = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
        [0.7, 0.8, 0.9],
    ]

    result = vector_store.store_chunks(
        chunks=chunks,
        vectors=vectors,
        source="postgres.md",
    )

    assert result == 3

    assert len(captured_points) == 3

    point_ids = [
        point.id
        for point in captured_points
    ]

    assert len(point_ids) == len(set(point_ids))


def test_store_chunks_preserves_source_and_chunk_metadata(
    monkeypatch,
):
    captured_points = []

    def fake_upsert(
        collection_name,
        points,
    ):
        captured_points.extend(points)

    monkeypatch.setattr(
        vector_store.client,
        "upsert",
        fake_upsert,
    )

    chunks = [
        "PostgreSQL supports transactions.",
        "PostgreSQL supports indexes.",
    ]

    vectors = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]

    result = vector_store.store_chunks(
        chunks=chunks,
        vectors=vectors,
        source="postgres.md",
    )

    assert result == 2

    assert len(captured_points) == 2

    first_payload = captured_points[0].payload
    second_payload = captured_points[1].payload

    assert first_payload["source"] == "postgres.md"
    assert first_payload["chunk_id"] == 0
    assert first_payload["text"] == chunks[0]

    assert second_payload["source"] == "postgres.md"
    assert second_payload["chunk_id"] == 1
    assert second_payload["text"] == chunks[1]


def test_store_chunks_uses_correct_collection(
    monkeypatch,
):
    captured_collection = None

    def fake_upsert(
        collection_name,
        points,
    ):
        nonlocal captured_collection
        captured_collection = collection_name

    monkeypatch.setattr(
        vector_store.client,
        "upsert",
        fake_upsert,
    )

    vector_store.store_chunks(
        chunks=["Test chunk"],
        vectors=[[0.1, 0.2, 0.3]],
        source="test.md",
    )

    assert (
        captured_collection
        == vector_store.COLLECTION_NAME
    )