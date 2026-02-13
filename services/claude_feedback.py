# services/claude_feedback.py
from __future__ import annotations
from typing import List
import anthropic

from config import ANTHROPIC_MAX_TOKENS, ANTHROPIC_TEMPERATURE

def list_anthropic_models(client_claude: anthropic.Anthropic) -> List[str]:
    try:
        page = client_claude.models.list(limit=100)
        return [m.id for m in page.data if getattr(m, "id", None)]
    except Exception:
        return []

def get_resume_feedback_from_claude(client_claude: anthropic.Anthropic, resume_text: str, model_id: str) -> str:
    system_prompt = "You're a career coach reviewing resumes for clarity, impact, and relevance."
    user_prompt = f"""Evaluate the following resume:

{resume_text}

Give me:
1. 3–5 specific improvement suggestions
2. Weak or vague bullet points, if any
3. Suggestions for tailoring to roles like: data analyst, product manager, ML engineer.
Return your response in a clear bullet list.
"""

    resp = client_claude.messages.create(
        model=model_id,
        system=system_prompt,
        max_tokens=ANTHROPIC_MAX_TOKENS,
        temperature=ANTHROPIC_TEMPERATURE,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return "".join(
        block.text for block in resp.content
        if getattr(block, "type", None) == "text"
    ).strip()

