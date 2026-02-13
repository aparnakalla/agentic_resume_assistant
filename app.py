# app.py
import io
import streamlit as st
from docx import Document
import anthropic
from openai import OpenAI

from config import get_openai_key, get_anthropic_key, get_anthropic_model_default
from services.openai_bullets import generate_bullet_points
from services.claude_feedback import list_anthropic_models, get_resume_feedback_from_claude
from docx_ops.replace_project import replace_first_project_safely
from docx_ops.extract_text import extract_text_from_docx

# =========================
# Page Config
# =========================
st.set_page_config(page_title="Agentic Resume Assistant", layout="centered")

# =========================
# Keys / Clients
# =========================
OPENAI_KEY = get_openai_key()
ANTHROPIC_KEY = get_anthropic_key()

if not OPENAI_KEY:
    st.error("Missing OPENAI_API_KEY in Streamlit secrets.")
    st.stop()

if not ANTHROPIC_KEY:
    st.error("Missing ANTHROPIC_API_KEY in Streamlit secrets.")
    st.stop()

client_openai = OpenAI(api_key=OPENAI_KEY)
client_claude = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

# =========================
# Session State
# =========================
for k in ["resume_text", "feedback", "updated_doc_bytes", "assumptions", "missing_questions", "generated_bullets"]:
    st.session_state.setdefault(k, None)

def reset_outputs():
    for k in ["resume_text", "feedback", "updated_doc_bytes", "assumptions", "missing_questions", "generated_bullets"]:
        st.session_state[k] = None

# =========================
# UI
# =========================
st.title("🤖 Agentic AI Resume Assistant")
st.markdown("Upload your resume, replace the first project, and get OpenAI + Claude feedback.")

uploaded_file = st.file_uploader("📄 Upload your `.docx` resume", type=["docx"], key="resume_uploader")

if uploaded_file is None:
    reset_outputs()
    st.info("Upload a resume to begin.")
    st.stop()

st.success("✅ Resume uploaded successfully!")

st.subheader("🛠️ Replace First Project")
subject = st.text_input(
    "Project Title",
    placeholder="Business Analytics Toolbox – Trends and Transitions in Men's College Basketball | Jan 2024 – May 2024",
)
description = st.text_area("Project Description", height=150)
github_url = st.text_input("GitHub Repository URL (optional)")

st.subheader("🧠 Claude Model")

@st.cache_data(ttl=300)
def cached_model_list():
    return list_anthropic_models(client_claude)

available_models = cached_model_list()

if available_models:
    default_model = get_anthropic_model_default()
    if default_model not in available_models:
        default_model = available_models[0]
    claude_model = st.selectbox(
        "Pick a Claude model (this list is what your API key can access):",
        options=available_models,
        index=available_models.index(default_model),
    )
else:
    st.warning(
        "Could not list Anthropic models for this key. "
        "We will try a fallback model ID, but it may fail if your key lacks access."
    )
    claude_model = get_anthropic_model_default()

if st.button("✨ Update Resume & Get Feedback"):
    if not subject.strip():
        st.error("Please enter a Project Title.")
        st.stop()

    with st.spinner("Generating bullet points using OpenAI (structured JSON)..."):
        bullets, assumptions, missing_qs = generate_bullet_points(
            client_openai=client_openai,
            subject=subject,
            description=description,
            github_url=github_url,
        )
        st.session_state["generated_bullets"] = bullets
        st.session_state["assumptions"] = assumptions
        st.session_state["missing_questions"] = missing_qs

    with st.spinner("Replacing the first project in your resume..."):
        doc = Document(uploaded_file)
        updated_doc = replace_first_project_safely(doc, subject, bullets)

        buf = io.BytesIO()
        updated_doc.save(buf)
        updated_bytes = buf.getvalue()

        resume_text = extract_text_from_docx(io.BytesIO(updated_bytes))

    with st.spinner(f"Getting feedback from Claude ({claude_model})..."):
        try:
            feedback = get_resume_feedback_from_claude(client_claude, resume_text, claude_model)
        except anthropic.NotFoundError:
            st.error(
                f"Model '{claude_model}' is not available for your API key. "
                "Pick a different model from the dropdown (if available), or check your Anthropic plan/access."
            )
            st.stop()

    st.session_state["updated_doc_bytes"] = updated_bytes
    st.session_state["resume_text"] = resume_text
    st.session_state["feedback"] = feedback

# =========================
# Render outputs
# =========================
if st.session_state["generated_bullets"]:
    st.subheader("🧾 Generated Bullets")
    st.write("\n".join([f"• {b}" for b in st.session_state["generated_bullets"]]))

    if st.session_state["missing_questions"]:
        st.info("Missing info (optional) — answering these can make bullets stronger:")
        for q in st.session_state["missing_questions"]:
            st.write(f"- {q}")

    if st.session_state["assumptions"]:
        st.warning("Assumptions the model avoided putting into bullets:")
        for a in st.session_state["assumptions"]:
            st.write(f"- {a}")

if st.session_state["resume_text"]:
    st.subheader("✅ Updated Resume Preview")
    st.text_area("Resume Text", st.session_state["resume_text"], height=300)

    st.download_button(
        label="📥 Download Updated Resume",
        data=st.session_state["updated_doc_bytes"],
        file_name="Updated_Resume.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    st.subheader("💬 Claude's Feedback")
    st.markdown(st.session_state["feedback"])

