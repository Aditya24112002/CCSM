from io import BytesIO
from pathlib import Path


def extract_document_text(filename: str, content: bytes) -> str:
    extension = Path(filename or '').suffix.lower()

    if extension in {'.txt', '.eml', '.csv'}:
        return content.decode('utf-8', errors='replace').strip()

    if extension == '.pdf':
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(content))
        return '\n\n'.join(page.extract_text() or '' for page in reader.pages).strip()

    if extension == '.docx':
        from docx import Document

        document = Document(BytesIO(content))
        return '\n'.join(paragraph.text for paragraph in document.paragraphs).strip()

    return content.decode('utf-8', errors='replace').strip()
