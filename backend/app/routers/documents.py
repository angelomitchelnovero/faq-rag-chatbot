"""
Document management endpoints.

POST   /documents/upload             - upload a PDF, extract text, chunk it, embed it, store in ChromaDB
GET    /documents                     - list all uploaded documents and their status
DELETE /documents/{id}                - remove a document and its chunks from the vector store
GET    /documents/{id}/download       - download the current PDF (public - linked from chat citations)
GET    /documents/{id}/raw            - get the raw extracted text (admin only)
PUT    /documents/{id}/raw            - edit the raw text; re-chunks, re-embeds, and regenerates the PDF

Naming convention on disk (in settings.upload_dir):
  {document_id}.pdf          - the actual PDF file (original, or regenerated after an edit)
  {document_id}.raw.txt      - the raw text currently backing that PDF's chunks/embeddings
"""
import os

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import require_admin
from app.models.document import Document
from app.models.schemas import DocumentResponse, RawTextResponse, RawTextUpdate
from app.models.user import User
from app.services.pdf_service import extract_text_from_pdf, write_text_to_pdf
from app.services.chunking import chunk_text
from app.services import vector_store

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf"}


def _pdf_path(document_id: str) -> str:
    return os.path.join(settings.upload_dir, f"{document_id}.pdf")


def _raw_text_path(document_id: str) -> str:
    return os.path.join(settings.upload_dir, f"{document_id}.raw.txt")


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

    # Save a DB record up front so we can report status even if processing fails partway
    doc = Document(filename=file.filename, status="processing")
    db.add(doc)
    db.commit()
    db.refresh(doc)

    file_path = _pdf_path(doc.id)
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Extract -> chunk -> embed -> store
        text = extract_text_from_pdf(file_path)
        if not text.strip():
            raise ValueError("No extractable text found in this PDF (it may be a scanned image).")

        chunks = chunk_text(text)
        num_stored = vector_store.add_chunks(document_id=doc.id, filename=doc.filename, chunks=chunks)

        # Save the raw text alongside it, so it can be viewed/edited later in admin
        with open(_raw_text_path(doc.id), "w", encoding="utf-8") as f:
            f.write(text)

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

    for path in (_pdf_path(document_id), _raw_text_path(document_id)):
        if os.path.exists(path):
            os.remove(path)

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

    file_path = _pdf_path(document_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="The file is no longer available.")

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=doc.filename,  # browser will save it under the original name
    )


@router.get("/{document_id}/raw", response_model=RawTextResponse)
def get_raw_text(
    document_id: str,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    _get_document_or_404(document_id, db)

    path = _raw_text_path(document_id)
    if not os.path.exists(path):
        raise HTTPException(
            status_code=404,
            detail="No editable text is available for this document (it may have failed processing).",
        )

    with open(path, "r", encoding="utf-8") as f:
        return RawTextResponse(text=f.read())


@router.put("/{document_id}/raw", response_model=DocumentResponse)
def update_raw_text(
    document_id: str,
    payload: RawTextUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """
    Edit a document's raw text. Re-chunks and re-embeds the new text, and
    regenerates the PDF file so the download link reflects the edit too.

    Note: the regenerated PDF is a clean reflow of the text, not a pixel
    copy of the original layout/fonts/images.

    Operations are ordered so that if anything fails partway, the document's
    existing (working) file and chunks are left untouched rather than
    corrupted or half-updated.
    """
    doc = _get_document_or_404(document_id, db)

    new_text = payload.text.strip()
    if not new_text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    new_chunks = chunk_text(new_text)
    tmp_pdf_path = _pdf_path(document_id) + ".tmp"

    try:
        # 1. Build the new PDF into a temp file first - if this fails, nothing real changes yet
        write_text_to_pdf(tmp_pdf_path, new_text)

        # 2. Swap out the vector store contents for this document
        vector_store.delete_document_chunks(document_id)
        num_stored = vector_store.add_chunks(document_id=document_id, filename=doc.filename, chunks=new_chunks)

        # 3. Only now that everything succeeded, replace the real files
        os.replace(tmp_pdf_path, _pdf_path(document_id))
        with open(_raw_text_path(document_id), "w", encoding="utf-8") as f:
            f.write(new_text)

        doc.num_chunks = num_stored
        doc.status = "ready"
        doc.error_message = None
        db.commit()
        db.refresh(doc)
        return doc

    except Exception as e:
        if os.path.exists(tmp_pdf_path):
            os.remove(tmp_pdf_path)
        raise HTTPException(status_code=500, detail=f"Failed to save changes: {e}")
