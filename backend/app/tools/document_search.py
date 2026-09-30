from langchain_core.tools import tool

from backend.app.rag.search import search_similar_chunks


@tool
def document_search(query: str) -> str:
    """
    Search the knowledge base for information relevant
    to the user's question.

    Use this tool when the user asks about information
    contained in the available documents.
    """

    results = search_similar_chunks(
        query=query,
        top_k=3
    )

    if not results:
        return "No relevant information was found."

    formatted_results = []

    for result in results:

        formatted_results.append(
            (
                f"Source: {result['source']}\n"
                f"Chunk ID: {result['chunk_id']}\n"
                f"Relevance Score: {result['score']:.4f}\n"
                f"Content:\n{result['text']}"
            )
        )

    return "\n\n".join(formatted_results)