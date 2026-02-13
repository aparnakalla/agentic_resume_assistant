# utils/bullets.py
from __future__ import annotations
from typing import List
import re

def clean_bullets(text: str, max_bullets: int = 3) -> List[str]:
    if not text:
        return []

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    bullets: List[str] = []

    for ln in lines:
        ln2 = ln.lstrip("•").lstrip("-").strip()
        # remove leading "1. " or "1) "
        if len(ln2) >= 3 and ln2[0].isdigit() and ln2[1:3] in [". ", ") "]:
            ln2 = ln2[3:].strip()
        if ln2:
            bullets.append(ln2)

    return bullets[:max_bullets]


def normalize_bullets(bullets: List[str], max_chars: int = 160, max_bullets: int = 3) -> List[str]:
    """Ensures bullets are 1-line, trimmed, and reasonably short."""
    out: List[str] = []
    for b in bullets[:max_bullets]:
        b = re.sub(r"\s+", " ", (b or "").strip())
        if not b:
            continue
        if len(b) > max_chars:
            b = b[: max_chars - 1].rstrip() + "…"
        out.append(b)
    return out

