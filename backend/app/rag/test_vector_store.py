from backend.app.rag.vector_store import (
    create_collection,
    collection_exists,
    COLLECTION_NAME
)


print("\nQdrant Vector Store Test")
print("=" * 50)


create_collection()


assert collection_exists()


print(
    f"\nCollection '{COLLECTION_NAME}' exists."
)

print("\nQdrant connection test PASSED")