from pathlib import Path


def load_document(file_path: str):
    """
    Load a text/Markdown document and return
    its content and metadata.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    content = path.read_text(
        encoding="utf-8"
    )

    return {
        "content": content,
        "metadata": {
            "source": path.name
        }
    }