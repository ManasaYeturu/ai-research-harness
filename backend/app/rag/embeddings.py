from langchain_ollama import OllamaEmbeddings


EMBEDDING_MODEL = "nomic-embed-text"


embeddings = OllamaEmbeddings(
    model=EMBEDDING_MODEL
)


def generate_embedding(text: str):
    """
    Generate an embedding vector for a single piece of text.
    """

    if not text or not text.strip():
        raise ValueError(
            "Text cannot be empty"
        )

    return embeddings.embed_query(text)


def generate_embeddings(texts: list[str]):
    """
    Generate embedding vectors for multiple texts.
    """

    if not texts:
        raise ValueError(
            "Texts cannot be empty"
        )

    return embeddings.embed_documents(texts)