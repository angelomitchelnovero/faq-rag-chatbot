"""
File storage service (Supabase Storage).

Stores the PDFs (original uploads and admin-regenerated versions) and
their raw extracted text. Files live in a Supabase Storage bucket instead
of local disk, so they survive backend restarts/redeploys on platforms
with ephemeral disks (e.g. Render's free tier).
"""
from supabase import create_client, Client

from app.config import settings

_client: Client | None = None
_bucket_ready = False


def _get_client() -> Client:
    global _client, _bucket_ready
    if _client is None:
        _client = create_client(settings.supabase_url, settings.supabase_service_role_key)

    if not _bucket_ready:
        _ensure_bucket_exists(_client)
        _bucket_ready = True

    return _client


def _ensure_bucket_exists(client: Client) -> None:
    """Create the storage bucket if it doesn't already exist. Safe to call repeatedly."""
    try:
        existing = [b.name for b in client.storage.list_buckets()]
        if settings.supabase_storage_bucket not in existing:
            client.storage.create_bucket(settings.supabase_storage_bucket, options={"public": False})
    except Exception:
        # If this fails (e.g. already exists, or a race with another instance
        # starting up at the same time), later calls will surface any real
        # problem anyway - no need to hard-fail startup over this.
        pass


def _pdf_key(document_id: str) -> str:
    return f"{document_id}.pdf"


def _raw_text_key(document_id: str) -> str:
    return f"{document_id}.raw.txt"


def upload_pdf(document_id: str, file_bytes: bytes) -> None:
    client = _get_client()
    client.storage.from_(settings.supabase_storage_bucket).upload(
        _pdf_key(document_id),
        file_bytes,
        file_options={"content-type": "application/pdf", "upsert": "true"},
    )


def download_pdf(document_id: str) -> bytes | None:
    client = _get_client()
    try:
        return client.storage.from_(settings.supabase_storage_bucket).download(_pdf_key(document_id))
    except Exception:
        return None


def upload_raw_text(document_id: str, text: str) -> None:
    client = _get_client()
    client.storage.from_(settings.supabase_storage_bucket).upload(
        _raw_text_key(document_id),
        text.encode("utf-8"),
        file_options={"content-type": "text/plain; charset=utf-8", "upsert": "true"},
    )


def download_raw_text(document_id: str) -> str | None:
    client = _get_client()
    try:
        data = client.storage.from_(settings.supabase_storage_bucket).download(_raw_text_key(document_id))
        return data.decode("utf-8")
    except Exception:
        return None


def delete_files(document_id: str) -> None:
    client = _get_client()
    try:
        client.storage.from_(settings.supabase_storage_bucket).remove(
            [_pdf_key(document_id), _raw_text_key(document_id)]
        )
    except Exception:
        pass
