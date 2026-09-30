from backend.app.rag.loader import load_document
from backend.app.rag.chunker import chunk_text
from backend.app.rag.embeddings import (
    generate_embedding,
    generate_embeddings
)


FILE_PATH = "knowledge/documents/postgres.md"


document = load_document(FILE_PATH)


chunks = chunk_text(
    document["content"],
    chunk_size=300
)


print("\nEmbedding test")
print("=" * 50)

print("Number of chunks:", len(chunks))


# --------------------------------------------------
# Test one embedding
# --------------------------------------------------

first_chunk = chunks[0]

vector = generate_embedding(first_chunk)


print("\nSingle embedding")
print("-" * 50)

print("Chunk length:", len(first_chunk))
print("Vector type:", type(vector))
print("Vector dimensions:", len(vector))

print("First 10 values:")
print(vector[:10])


assert vector
assert isinstance(vector, list)
assert len(vector) > 0


# --------------------------------------------------
# Test multiple embeddings
# --------------------------------------------------

vectors = generate_embeddings(chunks)


print("\nMultiple embeddings")
print("-" * 50)

print("Number of chunks:", len(chunks))
print("Number of vectors:", len(vectors))
print("Vector dimensions:", len(vectors[0]))


assert len(vectors) == len(chunks)

assert all(
    isinstance(vector, list)
    for vector in vectors
)

assert all(
    len(vector) == len(vectors[0])
    for vector in vectors
)


print("\nEmbedding test PASSED")