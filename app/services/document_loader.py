from pathlib import Path
from pypdf import PdfReader
from docx import Document


def load_document(file_path: Path) -> str:
    if file_path.suffix.lower() == ".pdf":
        return _load_pdf(file_path)
    elif file_path.suffix.lower() == ".docx":
        return _load_docx(file_path)
    elif file_path.suffix.lower() in [".txt", ".md"]:
        return file_path.read_text(encoding="utf-8")
    else:
        raise ValueError("Format de fichier non supporté")


def _load_pdf(path: Path) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _load_docx(path: Path) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)
