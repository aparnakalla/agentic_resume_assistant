from __future__ import annotations
from typing import List
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT


def replace_first_project_safely(doc: Document, new_title: str, new_bullets: List[str]) -> Document:
    def delete_paragraph(paragraph):
        p = paragraph._element
        p.getparent().remove(p)
        paragraph._p = paragraph._element = None

    def format_title(paragraph, text):
        run = paragraph.add_run(text)
        run.bold = True
        run.font.size = Pt(12)
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        paragraph.paragraph_format.space_after = Pt(2)
        paragraph.paragraph_format.space_before = Pt(6)

    def format_bullet(paragraph, text):
        run = paragraph.add_run(f"• {text}")
        run.font.size = Pt(10.5)
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        paragraph.paragraph_format.left_indent = Inches(0.25)
        paragraph.paragraph_format.first_line_indent = Inches(-0.15)
        paragraph.paragraph_format.space_after = Pt(1)
        paragraph.paragraph_format.space_before = Pt(0)

    def is_section_header(text: str) -> bool:
        t = text.strip()
        return t.isupper() and len(t) > 5

    def is_bullet(text: str) -> bool:
        return text.strip().startswith("•")

    def is_title_like(para) -> bool:
        # Bold OR looks like "Project – Description | Dates"
        if any(run.bold for run in para.runs if run.text.strip()):
            return True
        t = para.text.strip()
        return (
            " – " in t
            or " - " in t
            or "|" in t
        )

    # -----------------------------
    # 1. Find PROJECT EXPERIENCE
    # -----------------------------
    header_idx = None
    for i, para in enumerate(doc.paragraphs):
        if "PROJECT EXPERIENCE" in para.text.upper():
            header_idx = i
            break

    if header_idx is None:
        raise ValueError("PROJECT EXPERIENCE section not found")

    # -----------------------------
    # 2. Identify start of summary bullets
    # -----------------------------
    i = header_idx + 1
    while i < len(doc.paragraphs) and not doc.paragraphs[i].text.strip():
        i += 1

    summary_start = i if i < len(doc.paragraphs) and is_bullet(doc.paragraphs[i].text) else None

    # -----------------------------
    # 3. Find first actual project title
    # -----------------------------
    first_title_idx = None
    for j in range(i, len(doc.paragraphs)):
        if is_title_like(doc.paragraphs[j]):
            first_title_idx = j
            break

    if first_title_idx is None:
        raise ValueError("Could not locate first project title")

    # -----------------------------
    # 4. Find end of first project block
    # -----------------------------
    end_idx = len(doc.paragraphs)
    for k in range(first_title_idx + 1, len(doc.paragraphs)):
        txt = doc.paragraphs[k].text.strip()
        if not txt:
            continue
        if is_section_header(txt):
            end_idx = k
            break
        if is_title_like(doc.paragraphs[k]):
            end_idx = k
            break

    # -----------------------------
    # 5. Delete summary + first project
    # -----------------------------
    delete_start = summary_start if summary_start is not None else first_title_idx

    for idx in reversed(range(delete_start, end_idx)):
        delete_paragraph(doc.paragraphs[idx])

    anchor = doc.paragraphs[delete_start]

    # -----------------------------
    # 6. Insert new project cleanly
    # -----------------------------
    for bullet in reversed(new_bullets):
        p = anchor.insert_paragraph_before("")
        format_bullet(p, bullet)

    title_p = anchor.insert_paragraph_before("")
    format_title(title_p, new_title)

    return doc
