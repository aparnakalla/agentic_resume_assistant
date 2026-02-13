# services/openai_bullets.py
from __future__ import annotations
from typing import List, Optional, Dict, Any, Tuple

from openai import OpenAI

from config import get_openai_model, OPENAI_TEMPERATURE, MIN_BULLETS, MAX_BULLETS, MAX_BULLET_CHARS
from utils.schema import safe_load_json, validate_bullets_payload, SchemaError
from utils.bullets import normalize_bullets

def build_bullets_prompt(subject: str, description: str, github_url: str) -> str:
    return f"""
You are a resume expert. Generate 2–3 concise, high-impact resume bullet points for the project.

Rules:
- Return ONLY valid JSON (no markdown, no extra text).
- Bullets must be 1 line each, action-verb led, and specific.
- Do NOT invent metrics. If a metric is missing, either omit it or put it under "missing_info_questions".
- If you must make an assumption, put it under "assumptions" (do not put it in bullets).

Return this JSON schema:
{{
  "bullets": ["...","..."],
  "assumptions": [],
  "missing_info_questions": []
}}

Project Title: {subject}
Project Description: {description}
GitHub (optional): {github_url}
""".strip()

def generate_bullet_points(
    client_openai: OpenAI,
    subject: str,
    description: str,
    github_url: str = "",
) -> Tuple[List[str], List[str], List[str]]:
    """
    Returns (bullets, assumptions, missing_questions)
    """
    prompt = build_bullets_prompt(subject, description, github_url)
    model_name = get_openai_model()

    resp = client_openai.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=OPENAI_TEMPERATURE,
    )

    raw = (resp.choices[0].message.content or "").strip()

    try:
        payload = safe_load_json(raw)
        bullets, assumptions, missing = validate_bullets_payload(payload, min_bullets=MIN_BULLETS, max_bullets=MAX_BULLETS)
        bullets = normalize_bullets(bullets, max_chars=MAX_BULLET_CHARS, max_bullets=MAX_BULLETS)
        return bullets, assumptions, missing
    except SchemaError:
        # fallback: treat raw as text bullets
        # keep it conservative
        fallback = normalize_bullets([ln.strip("• ").strip() for ln in raw.splitlines() if ln.strip()], max_chars=MAX_BULLET_CHARS)
        fallback = fallback[:MAX_BULLETS]
        if len(fallback) < MIN_BULLETS:
            fallback = [
                "Built an end-to-end resume editing workflow, emphasizing reliability, formatting accuracy, and measurable output quality.",
                "Implemented LLM-driven bullet generation with structured outputs and validation to reduce formatting errors and hallucinated claims.",
            ][:MAX_BULLETS]
        return fallback, [], []

