# config.py
import streamlit as st

def get_openai_key() -> str:
    return st.secrets.get("OPENAI_API_KEY", "")

def get_anthropic_key() -> str:
    return st.secrets.get("ANTHROPIC_API_KEY", "")

def get_openai_model() -> str:
    return st.secrets.get("OPENAI_MODEL", "gpt-4o-mini")

def get_anthropic_model_default() -> str:
    # fallback if model list isn't available
    return st.secrets.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")

OPENAI_TEMPERATURE = 0.4
ANTHROPIC_TEMPERATURE = 0.4
ANTHROPIC_MAX_TOKENS = 1000
MAX_BULLETS = 3
MIN_BULLETS = 2
MAX_BULLET_CHARS = 160

