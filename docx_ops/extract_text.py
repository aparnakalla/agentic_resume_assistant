# docx_ops/extract_text.py
from __future__ import annotations
from docx import Document

def extract_text_from_docx(docx_file) -> str:
    doc = Document(docx_file)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

