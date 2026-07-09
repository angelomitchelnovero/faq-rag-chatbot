"""
Vector store service (ChromaDB).

Handles embedding text chunks and storing/retrieving them by similarity.
Uses ChromaDB's built-in ONNX embedding function (all-MiniLM-L6-v2) —
free, runs locally, no API calls or PyTorch required.
"""
import chromadb
from chromadb.utils import embedding_functions

from app.config import settings

_client = None
_collection = None

COLLECTION_NAME = "faq_documents"


def get_collection():
    """Lazily initialize and return the ChromaDB collection (singleton)."""
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=settings.chroma_dir)
        embed_fn = embedding_functions.DefaultEmbeddingFunction()
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embed_fn,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_chunks(document_id: str, filename: str, chunks: list[str]) -> int:
    """Embed and store chunks for a document. Returns number of chunks stored."""
    if not chunks:
        return 0

    collection = get_collection()
    ids = [f"{document_id}::chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {"document_id": document_id, "filename": filename, "chunk_index": i}
        for i in range(len(chunks))
    ]

    collection.add(ids=ids, documents=chunks, metadatas=metadatas)
    return len(chunks)


def delete_document_chunks(document_id: str) -> None:
    """Remove all chunks belonging to a document (used when a document is deleted)."""
    collection = get_collection()
    collection.delete(where={"document_id": document_id})


def query_similar_chunks(query_text: str, top_k: int = 4) -> list[dict]:
    """
    Return the top_k most relevant chunks for a query, each as:
    {"text": ..., "filename": ..., "document_id": ..., "distance": ...}
    """
    collection = get_collection()
    results = collection.query(query_texts=[query_text], n_results=top_k)

    chunks = []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(documents, metadatas, distances):
        chunks.append(
            {
                "text": doc,
                "filename": meta.get("filename"),
                "document_id": meta.get("document_id"),
                "distance": dist,
            }
        )
    return chunks
