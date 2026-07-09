"""
PDF text extraction.

Uses pdfplumber (better layout/table handling) as the primary method,
falling back to pypdf if pdfplumber fails on a given file (e.g. some
malformed or unusually-encoded PDFs).
"""
import pdfplumber
from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text from a PDF file, page by page, joined with newlines."""
    text = _extract_with_pdfplumber(file_path)
    if text.strip():
        return text

    # Fallback if pdfplumber got nothing (e.g. unusual PDF structure)
    return _extract_with_pypdf(file_path)


def _extract_with_pdfplumber(file_path: str) -> str:
    pages_text = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            pages_text.append(page_text)
    return "\n\n".join(pages_text)


def _extract_with_pypdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages_text)
