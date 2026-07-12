"""
PDF text extraction and generation - pure in-memory (bytes in, bytes/str out).

No local file paths are used here anymore. This matters because the backend
is designed to be stateless (Render's free tier has ephemeral disk) - the
only persistent storage is Supabase (Postgres + Storage).

Extraction uses pdfplumber (better layout/table handling) as the primary
method, falling back to pypdf if pdfplumber fails on a given file (e.g.
some malformed or unusually-encoded PDFs).

Generation (generate_pdf_from_text) is used when an admin edits a document's
raw text - it produces a clean, simply-formatted PDF from that text.
Note: this does NOT preserve the original file's exact layout, fonts, or
images. It's a plain reflow of the edited text into a readable PDF.
"""
import io

import pdfplumber
from pypdf import PdfReader
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from xml.sax.saxutils import escape


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from PDF bytes, page by page, joined with newlines."""
    text = _extract_with_pdfplumber(file_bytes)
    if text.strip():
        return text

    # Fallback if pdfplumber got nothing (e.g. unusual PDF structure)
    return _extract_with_pypdf(file_bytes)


def _extract_with_pdfplumber(file_bytes: bytes) -> str:
    pages_text = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            pages_text.append(page_text)
    return "\n\n".join(pages_text)


def _extract_with_pypdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages_text)


def generate_pdf_from_text(text: str) -> bytes:
    """
    Generate a simple, cleanly-formatted PDF from plain text and return its
    bytes. Paragraphs are separated by blank lines in the source text.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
    )
    styles = getSampleStyleSheet()
    body_style = styles["BodyText"]
    body_style.leading = 15

    story = []
    paragraphs = text.split("\n\n")
    for para in paragraphs:
        cleaned = para.strip()
        if not cleaned:
            continue
        safe_text = escape(cleaned).replace("\n", "<br/>")
        story.append(Paragraph(safe_text, body_style))
        story.append(Spacer(1, 12))

    if not story:
        story = [Paragraph("(This document is empty.)", body_style)]

    doc.build(story)
    return buffer.getvalue()
