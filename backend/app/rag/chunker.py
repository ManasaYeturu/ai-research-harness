def chunk_text(
    text: str,
    chunk_size: int = 300
):
    """
    Split a document into chunks while preserving
    paragraph boundaries.

    Paragraphs are combined until adding another
    paragraph would exceed the target chunk size.
    """

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0"
        )

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:

        if not current_chunk:
            current_chunk = paragraph
            continue

        candidate = (
            current_chunk
            + "\n\n"
            + paragraph
        )

        if len(candidate) <= chunk_size:
            current_chunk = candidate

        else:
            chunks.append(current_chunk)
            current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks