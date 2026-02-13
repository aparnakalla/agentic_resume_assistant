# docx_ops/replace_project.py
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
        paragraph.paragraph_format.space_after = Pt(0)
        paragraph.paragraph_format.space_before = Pt(0)

    def format_bullet(paragraph, text):
        run = paragraph.add_run(f"• {text}")
        run.font.size = Pt(10.5)
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        paragraph.paragraph_format.left_indent = Inches(0.25)
        paragraph.paragraph_format.first_line_indent = Inches(-0.15)
        paragraph.paragraph_format.space_after = Pt(0)
        paragraph.paragraph_format.space_before = Pt(0)

    new_bullets = [bp.strip() for bp in new_bullets if bp and bp.strip()]

    section_found = False
    start_idx = -1
    end_idx = -1

    for i, para in enumerate(doc.paragraphs):
        if "PROJECT EXPERIENCE" in para.text.upper():
            section_found = True
            continue

        if section_found and start_idx == -1 and para.text.strip():
            start_idx = i
            continue

        if section_found and start_idx != -1:
            if para.runs and para.runs[0].bold:
                end_idx = i
                break

    if not section_found:
        raise ValueError("Could not find 'PROJECT EXPERIENCE' section in the document.")
    if start_idx == -1:
        raise ValueError("Found 'PROJECT EXPERIENCE' but couldn't locate the first project entry below it.")

    if end_idx == -1:
        for j in range(start_idx + 1, len(doc.paragraphs)):
            if doc.paragraphs[j].text.strip() == "":
                end_idx = j
                break
        else:
            end_idx = len(doc.paragraphs)

    for idx in reversed(range(start_idx, end_idx)):
        delete_paragraph(doc.paragraphs[idx])

    insert_idx = start_idx

    for bullet in reversed(new_bullets):
        bullet_para = doc.paragraphs[insert_idx].insert_paragraph_before("")
        format_bullet(bullet_para, bullet)

    title_para = doc.paragraphs[insert_idx].insert_paragraph_before("")
    format_title(title_para, new_title)

    return doc

