"""
PDF text extraction and generation.

Extraction uses pdfplumber (better layout/table handling) as the primary
method, falling back to pypdf if pdfplumber fails on a given file (e.g.
some malformed or unusually-encoded PDFs).

Generation (write_text_to_pdf) is used when an admin edits a document's
raw text - it produces a clean, simply-formatted PDF from that text.
Note: this does NOT preserve the original file's exact layout, fonts, or
images. It's a plain reflow of the edited text into a readable PDF.
"""
import pdfplumber
from pypdf import PdfReader
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from xml.sax.saxutils import escape


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


def write_text_to_pdf(file_path: str, text: str) -> None:
    """
    Generate a simple, cleanly-formatted PDF from plain text, overwriting
    file_path. Paragraphs are separated by blank lines in the source text.
    """
    doc = SimpleDocTemplate(
        file_path,
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
        # Escape special XML characters (reportlab paragraphs use basic markup)
        # and turn single newlines within a paragraph into <br/> line breaks.
        safe_text = escape(cleaned).replace("\n", "<br/>")
        story.append(Paragraph(safe_text, body_style))
        story.append(Spacer(1, 12))

    if not story:
        story = [Paragraph("(This document is empty.)", body_style)]

    doc.build(story)
