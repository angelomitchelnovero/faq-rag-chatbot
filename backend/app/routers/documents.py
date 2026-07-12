"""
Document management endpoints.

POST   /documents/upload             - upload a PDF, extract text, chunk it, embed it, store
GET    /documents                     - list all uploaded documents and their status
DELETE /documents/{id}                - remove a document and its chunks
GET    /documents/{id}/download       - download the current PDF (public - linked from chat citations)
GET    /documents/{id}/raw            - get the raw extracted text (admin only)
PUT    /documents/{id}/raw            - edit the raw text; re-chunks, re-embeds, and regenerates the PDF

All persistent data (the PDF bytes, the raw text, the chunk embeddings)
lives in Supabase (Storage + Postgres/pgvector) rather than local disk,
so it survives backend restarts on hosts with ephemeral disk.
"""
import os

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.document import Document
from app.models.schemas import DocumentResponse, RawTextResponse, RawTextUpdate
from app.models.user import User
from app.services.pdf_service import extract_text_from_pdf, generate_pdf_from_text
from app.services.chunking import chunk_text
from app.services import vector_store, storage_service

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf"}


def _get_document_or_404(document_id: str, db: Session) -> Document:
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF files are supported right now.")

    doc = Document(filename=file.filename, status="processing")
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        file_bytes = file.file.read()

        text = extract_text_from_pdf(file_bytes)
        if not text.strip():
            raise ValueError("No extractable text found in this PDF (it may be a scanned image).")

        chunks = chunk_text(text)
        num_stored = vector_store.add_chunks(document_id=doc.id, filename=doc.filename, chunks=chunks)

        storage_service.upload_pdf(doc.id, file_bytes)
        storage_service.upload_raw_text(doc.id, text)

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
def list_documents(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    return db.query(Document).order_by(Document.uploaded_at.desc()).all()


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    doc = _get_document_or_404(document_id, db)

    vector_store.delete_document_chunks(document_id)
    storage_service.delete_files(document_id)

    db.delete(doc)
    db.commit()
    return {"status": "deleted", "id": document_id}


@router.get("/{document_id}/download")
def download_document(document_id: str, db: Session = Depends(get_db)):
    """
    Public endpoint - lets chat users download the current PDF behind a
    source citation. Not admin-gated since chat answers already expose the
    document's content; this just gives access to the underlying file.
    """
    doc = _get_document_or_404(document_id, db)

    file_bytes = storage_service.download_pdf(document_id)
    if file_bytes is None:
        raise HTTPException(status_code=404, detail="The file is no longer available.")

    return Response(
        content=file_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{doc.filename}"'},
    )


@router.get("/{document_id}/raw", response_model=RawTextResponse)
def get_raw_text(
    document_id: str,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    _get_document_or_404(document_id, db)

    text = storage_service.download_raw_text(document_id)
    if text is None:
        raise HTTPException(
            status_code=404,
            detail="No editable text is available for this document (it may have failed processing).",
        )

    return RawTextResponse(text=text)


@router.put("/{document_id}/raw", response_model=DocumentResponse)
def update_raw_text(
    document_id: str,
    payload: RawTextUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """
    Edit a document's raw text. Re-chunks and re-embeds the new text
    (atomically - old chunks are only replaced if the new ones are
    successfully stored) and regenerates the PDF file.

    Note: the regenerated PDF is a clean reflow of the text, not a pixel
    copy of the original layout/fonts/images.
    """
    doc = _get_document_or_404(document_id, db)

    new_text = payload.text.strip()
    if not new_text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    new_chunks = chunk_text(new_text)

    try:
        # 1. Atomically swap the chunk embeddings (source of truth for chat answers)
        num_stored = vector_store.replace_document_chunks(document_id, doc.filename, new_chunks)

        # 2. Regenerate the PDF and upload both files
        new_pdf_bytes = generate_pdf_from_text(new_text)
        storage_service.upload_pdf(document_id, new_pdf_bytes)
        storage_service.upload_raw_text(document_id, new_text)

        doc.num_chunks = num_stored
        doc.status = "ready"
        doc.error_message = None
        db.commit()
        db.refresh(doc)
        return doc

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save changes: {e}")
