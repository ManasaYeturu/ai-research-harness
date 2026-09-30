from backend.app.rag.loader import load_document


FILE_PATH = "knowledge/documents/postgres.md"


document = load_document(FILE_PATH)


print("\nDocument loaded successfully")
print("=" * 50)

print("Content:")
print(document["content"])

print("=" * 50)

print("Metadata:")
print(document["metadata"])


assert document["content"]

assert document["metadata"]["source"] == "postgres.md"


print("\nDocument loader test PASSED")