# utils/schema.py
from __future__ import annotations
from typing import Any, Dict, List, Tuple
import json
import re

class SchemaError(ValueError):
    pass

def _extract_json_object(text: str) -> str:
    """
    Extract the first {...} block from a string. Handles code fences.
    """
    if not text:
        raise SchemaError("Empty response")

    # remove ```json fences
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE | re.MULTILINE)

    # find first JSON object
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise SchemaError("No JSON object found in response")
    return cleaned[start : end + 1]

def safe_load_json(text: str) -> Dict[str, Any]:
    raw = _extract_json_object(text)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise SchemaError(f"Invalid JSON: {e}")

def validate_bullets_payload(payload: Dict[str, Any], min_bullets: int = 2, max_bullets: int = 3) -> Tuple[List[str], List[str], List[str]]:
    """
    Expected payload:
      { "bullets": [...], "assumptions": [...], "missing_info_questions": [...] }
    Returns: (bullets, assumptions, missing_questions)
    """
    if not isinstance(payload, dict):
        raise SchemaError("Payload is not an object")

    bullets = payload.get("bullets", [])
    assumptions = payload.get("assumptions", [])
    missing = payload.get("missing_info_questions", [])

    if not isinstance(bullets, list) or not all(isinstance(x, str) for x in bullets):
        raise SchemaError("'bullets' must be a list of strings")

    bullets = [b.strip() for b in bullets if b and b.strip()]
    if len(bullets) < min_bullets:
        raise SchemaError(f"Need at least {min_bullets} bullets")
    bullets = bullets[:max_bullets]

    if not isinstance(assumptions, list) or not all(isinstance(x, str) for x in assumptions):
        assumptions = []
    if not isinstance(missing, list) or not all(isinstance(x, str) for x in missing):
        missing = []

    assumptions = [a.strip() for a in assumptions if a and a.strip()]
    missing = [m.strip() for m in missing if m and m.strip()]

    return bullets, assumptions, missing

