"""
Vector store service (Postgres + pgvector).

Stores and retrieves document chunks by similarity, using Supabase's
Postgres database with the pgvector extension - instead of a separate
local ChromaDB (which doesn't survive restarts on ephemeral-disk hosts
like Render's free tier).

Embeddings are generated locally with fastembed (ONNX, no PyTorch, no
per-call API cost or network dependency once the model is cached).
"""
from fastembed import TextEmbedding
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, String, Integer, Text

from app.database import Base, SessionLocal

EMBEDDING_DIM = 384  # dimension of sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_embedding_model: TextEmbedding | None = None


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, nullable=False, index=True)
    filename = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=False)


def _get_embedding_model() -> TextEmbedding:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = TextEmbedding(model_name=EMBEDDING_MODEL_NAME)
    return _embedding_model


def _embed(texts: list[str]) -> list[list[float]]:
    model = _get_embedding_model()
    return [vec.tolist() for vec in model.embed(texts)]


def add_chunks(document_id: str, filename: str, chunks: list[str]) -> int:
    """Embed and store chunks for a document. Returns number of chunks stored."""
    if not chunks:
        return 0

    vectors = _embed(chunks)
    db = SessionLocal()
    try:
        for i, (chunk_text, vector) in enumerate(zip(chunks, vectors)):
            db.add(
                DocumentChunk(
                    document_id=document_id,
                    filename=filename,
                    chunk_index=i,
                    text=chunk_text,
                    embedding=vector,
                )
            )
        db.commit()
    finally:
        db.close()
    return len(chunks)


def delete_document_chunks(document_id: str) -> None:
    """Remove all chunks belonging to a document."""
    db = SessionLocal()
    try:
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
        db.commit()
    finally:
        db.close()


def replace_document_chunks(document_id: str, filename: str, chunks: list[str]) -> int:
    """
    Atomically swap out all chunks for a document (delete old + insert new
    in a single transaction). Used when an admin edits a document's text -
    if anything fails, the old chunks remain intact rather than being lost.
    """
    vectors = _embed(chunks) if chunks else []
    db = SessionLocal()
    try:
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
        for i, (chunk_text, vector) in enumerate(zip(chunks, vectors)):
            db.add(
                DocumentChunk(
                    document_id=document_id,
                    filename=filename,
                    chunk_index=i,
                    text=chunk_text,
                    embedding=vector,
                )
            )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    return len(chunks)


def query_similar_chunks(query_text: str, top_k: int = 4) -> list[dict]:
    """
    Return the top_k most relevant chunks for a query, each as:
    {"text": ..., "filename": ..., "document_id": ..., "distance": ...}
    """
    query_vector = _embed([query_text])[0]
    db = SessionLocal()
    try:
        results = (
            db.query(
                DocumentChunk,
                DocumentChunk.embedding.cosine_distance(query_vector).label("distance"),
            )
            .order_by("distance")
            .limit(top_k)
            .all()
        )
        return [
            {
                "text": chunk.text,
                "filename": chunk.filename,
                "document_id": chunk.document_id,
                "distance": float(dist),
            }
            for chunk, dist in results
        ]
    finally:
        db.close()
