"""
Text chunking.

Embeddings and LLM context work best with small, semantically coherent
chunks rather than whole documents. We use a simple sliding-window
word-based chunker with overlap, so context isn't lost at chunk boundaries.

Chunk size and overlap are conservative defaults tuned for FAQ-style
documents (policies, manuals, product docs). Feel free to tune later.
"""

DEFAULT_CHUNK_SIZE = 300   # words per chunk
DEFAULT_CHUNK_OVERLAP = 50  # words shared between consecutive chunks


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """Split text into overlapping word-based chunks."""
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    step = max(chunk_size - overlap, 1)  # guard against overlap >= chunk_size

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk = " ".join(chunk_words).strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks
