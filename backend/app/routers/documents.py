"""
Document management endpoints.

POST   /documents/upload   - upload a PDF, extract text, chunk it, embed it, store in ChromaDB
GET    /documents           - list all uploaded documents and their status
DELETE /documents/{id}      - remove a document and its chunks from the vector store
"""
import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.document import Document
from app.models.schemas import DocumentResponse
from app.services.pdf_service import extract_text_from_pdf
from app.services.chunking import chunk_text
from app.services import vector_store

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf"}


@router.post("/upload", response_model=DocumentResponse)
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF files are supported right now.")

    # Save a DB record up front so we can report status even if processing fails partway
    doc = Document(filename=file.filename, status="processing")
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Save the raw file to disk
    safe_name = f"{doc.id}{ext}"
    file_path = os.path.join(settings.upload_dir, safe_name)
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Extract -> chunk -> embed -> store
        text = extract_text_from_pdf(file_path)
        if not text.strip():
            raise ValueError("No extractable text found in this PDF (it may be a scanned image).")

        chunks = chunk_text(text)
        num_stored = vector_store.add_chunks(document_id=doc.id, filename=doc.filename, chunks=chunks)

        doc.status = "ready"
        doc.num_chunks = num_stored
        db.commit()
        db.refresh(doc)

    except Exception as e:
        doc.status = "failed"
        doc.error_message = str(e)
        db.commit()
        db.refresh(doc)

    return doc


@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.uploaded_at.desc()).all()


@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Remove chunks from ChromaDB
    vector_store.delete_document_chunks(document_id)

    # Remove the stored file from disk, if it still exists
    for f in os.listdir(settings.upload_dir):
        if f.startswith(document_id):
            os.remove(os.path.join(settings.upload_dir, f))

    db.delete(doc)
    db.commit()
    return {"status": "deleted", "id": document_id}
