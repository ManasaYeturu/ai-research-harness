from backend.app.rag.loader import load_document
from backend.app.rag.chunker import chunk_text


FILE_PATH = "knowledge/documents/postgres.md"


document = load_document(FILE_PATH)

chunks = chunk_text(
    document["content"],
    chunk_size=300
)


print("\nDocument chunking")
print("=" * 50)

print("Original characters:", len(document["content"]))
print("Number of chunks:", len(chunks))


for index, chunk in enumerate(chunks, start=1):

    print("\n" + "-" * 50)
    print(f"Chunk {index}")
    print("-" * 50)
    print(chunk)


assert len(chunks) > 1

assert all(
    len(chunk) <= 300
    for chunk in chunks
)


print("\nChunking test PASSED")