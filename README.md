
# Agentic AI Resume Assistant — CrewAI Refactor Branch

A **multi-agent AI system** that intelligently analyzes, critiques, and enhances technical resumes using a crew-based orchestration pattern with OpenAI and Anthropic APIs.

## 🎯 Overview

This branch (`feature/crewai-refactor`) implements a custom agent orchestration framework inspired by CrewAI principles. The system uses **two specialized agents** working in tandem:

1. **Bullet Writer Agent** (OpenAI) — Generates high-impact resume bullet points
2. **Resume Critic Agent** (Claude) — Provides detailed feedback and improvement suggestions

Users upload a DOCX resume, describe a project, and the system:
- ✨ Generates 2-3 action-verb-led, quantified bullet points
- 📋 Replaces the first project in the resume with AI-generated bullets
- 💬 Provides structured feedback on clarity, impact, and role-fit
- 📥 Downloads an updated resume

## ✨ Key Features

- **Multi-Agent Orchestration**: Custom `Crew` class orchestrates agents sequentially with context passing
- **Dual LLM Pipeline**: Combines OpenAI (bullet generation) + Claude (critique) for comprehensive feedback
- **Schema Validation**: Enforces structured JSON outputs to reduce hallucinations and formatting errors
- **Document Processing**: Safely extracts text and replaces project sections in DOCX files
- **Streamlit UI**: Interactive web interface for resume management
- **Fallback Handling**: Graceful degradation if LLM outputs don't match expected schema

## 📁 Project Structure

```
agentic_resume_assistant/
├── app.py                    # Streamlit UI main entry point
├── config.py                 # Configuration & secrets management
├── requirements.txt          # Python dependencies
│
├── services/                 # Core orchestration logic
│   ├── crew.py              # Agent, Task, Crew classes + run_resume_crew()
│   ├── claude_feedback.py   # Claude API utilities
│   └── openai_bullets.py    # OpenAI API utilities
│
├── docx_ops/                # Document operations
│   ├── extract_text.py      # Extract text from DOCX
│   └── replace_project.py   # Replace first project in DOCX
│
├── utils/                   # Helper utilities
│   ├── schema.py           # JSON validation & schema enforcement
│   └── bullets.py          # Bullet formatting & normalization
│
└── tests/                  # Unit tests (placeholder)
```


## 🤖 Architecture & Workflow

### Agent & Task System

The system implements a custom crew orchestration inspired by CrewAI principles:

**Agent Class**: Defines role, goal, backstory, and LLM type (OpenAI or Anthropic)

**Task Class**: Encapsulates a specific job with description, expected output, and context from previous tasks

**Crew Class**: Orchestrates sequential execution:
- Runs each task through its assigned agent's LLM
- Passes outputs from previous tasks as context for subsequent tasks
- Returns all task outputs for post-processing

### Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INPUT                               │
│  • Project Title                                            │
│  • Project Description                                      │
│  • GitHub URL (optional)                                    │
│  • Resume (DOCX file)                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            EXTRACT TEXT FROM DOCX                           │
│  docx_ops/extract_text.py                                   │
│  → Returns: plain text resume content                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          BULLET WRITER AGENT (OpenAI)                       │
│  services/crew.py → run_resume_crew()                       │
│                                                             │
│  Role: Resume Bullet Point Writer                           │
│  Goal: Generate 2-3 high-impact bullets                     │
│  LLM: gpt-4o-mini (configurable)                            │
│                                                             │
│  Input: Project details + description                       │
│  Processing:                                                │
│    • Enforces JSON schema output                            │
│    • Validates action-verb led bullets                      │
│    • Captures missing info & assumptions                    │
│  Output: {                                                  │
│    "bullets": ["Bullet 1", "Bullet 2"],                     │
│    "assumptions": [...],                                    │
│    "missing_info_questions": [...]                          │
│  }                                                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼ (output passed as context)
┌─────────────────────────────────────────────────────────────┐
│         RESUME CRITIC AGENT (Claude)                        │
│  services/crew.py → run_resume_crew()                       │
│                                                             │
│  Role: Senior Technical Recruiter                           │
│  Goal: Evaluate resume & provide feedback                   │
│  LLM: claude-3-5-sonnet-20241022 (configurable)             │
│                                                             │
│  Input: Full resume + Bullet Writer's output                │
│  Processing:                                                │
│    • Reviews entire resume context                          │
│    • Evaluates newly generated bullets                      │
│    • Suggests improvements & role-fit changes               │
│    • Provides role-tailoring advice                         │
│  Output: Structured feedback (markdown)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│       BULLET NORMALIZATION & VALIDATION                     │
│  utils/bullets.py & utils/schema.py                         │
│                                                             | 
│  • Enforce character limits (max 160 chars/bullet)          │
│  • Validate bullet count (2-3 bullets)                      │
│  • Safe truncation & line splitting                         │
│  • Fallback to safe defaults if schema invalid              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│        DOCUMENT PROCESSING & REPLACEMENT                    │
│  docx_ops/replace_project.py                                │
│                                                             │
│  • Load original DOCX file                                  │
│  • Find first project section                               │
│  • Replace with new AI-generated bullets                    │
│  • Preserve formatting & structure                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            STREAMLIT UI RENDERING                           │
│  app.py                                                     │
│                                                             │
│  Display:                                                   │
│  ✅ Generated Bullets                                       │
│  ⚠️  Assumptions & Missing Info                             │
│  📝 Updated Resume Preview                                  │
│  💬 Claude's Detailed Feedback                              │
│  📥 Download Button                                         |
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            USER DOWNLOADS UPDATED RESUME                    │
│  • Updated_Resume.docx with new bullets                     │
│  • Ready to submit to job applications                      │
└─────���─────────────────────────────────────────────────────┘
```

## 📝 Configuration Parameters

Located in `config.py`:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `OPENAI_TEMPERATURE` | 0.4 | Bullet generation creativity (lower = more focused) |
| `ANTHROPIC_TEMPERATURE` | 0.4 | Critique creativity (lower = more focused) |
| `ANTHROPIC_MAX_TOKENS` | 1000 | Max tokens for Claude response |
| `MIN_BULLETS` | 2 | Minimum generated bullets |
| `MAX_BULLETS` | 3 | Maximum generated bullets |
| `MAX_BULLET_CHARS` | 160 | Character limit per bullet |
| `OPENAI_MODEL` | gpt-4o-mini | OpenAI model for bullet generation |
| `ANTHROPIC_MODEL` | claude-3-5-sonnet-20241022 | Claude model for critique |

## 💡 Usage Example

### Step-by-Step

1. **Upload Resume**: Click to select your DOCX resume file
2. **Enter Project Details**:
   ```
   Project Title: "Built Real-time ML Recommendation Engine"
   
   Description: "Developed end-to-end ML pipeline using PyTorch and PostgreSQL 
   to power recommendation system. Optimized queries reducing latency by 40%. 
   Handled 1M+ daily requests with 99.9% uptime."
   
   GitHub URL: https://github.com/yourname/ml-recommendations
   ```
3. **Select Claude Model**: Choose from available models your API key can access
4. **Click "✨ Update Resume & Get Feedback"**
5. **Review Results**:
   - ✅ View 2-3 generated bullets
   - ⚠️ See missing info & assumptions (optional questions to strengthen bullets)
   - 💬 Read Claude's detailed feedback
6. **Download**: Click "📥 Download Updated Resume" to get your updated DOCX file

### Expected Output Example

**Generated Bullets:**
- Architected real-time ML pipeline processing 1M+ daily requests with 99.9% uptime
- Reduced query latency by 40% through PostgreSQL optimization and PyTorch model tuning
- Built recommendation engine serving personalized content to 500K+ active users

**Claude's Feedback:**
- ✨ Strong metric-driven bullets; quantified impact is excellent
- 🎯 Role-fit: Strong match for ML Engineer, decent fit for Data Scientist roles
- 💡 Suggestion: Add tech stack details (PyTorch, PostgreSQL versions) if space allows

## 🔧 Core Components

### `services/crew.py`

The heart of the multi-agent system:

```python
# Agent: Defines LLM-backed entity with role, goal, backstory, and LLM type
agent = Agent(
    role="Resume Bullet Point Writer",
    goal="Generate high-impact bullets",
    backstory="Expert resume writer at top tech companies...",
    llm="openai"  # or "anthropic"
)

# Task: Defines work to be done by an agent
task = Task(
    description="Generate 2-3 bullets for...",
    expected_output="Valid JSON with bullets array",
    agent=agent,
    context=[previous_task]  # Receive outputs from prior tasks
)

# Crew: Orchestrates sequential execution of tasks
crew = Crew(tasks=[task1, task2], claude_model="claude-3-5-sonnet-20241022")
outputs = crew.kickoff()  # Returns list of task outputs
```

### `docx_ops/`

Document manipulation utilities:

- **`extract_text.py`**: Parses DOCX files to plain text for LLM analysis
  ```python
  text = extract_text_from_docx(io.BytesIO(file_bytes))
  ```

- **`replace_project.py`**: Safely modifies DOCX structure, replacing first project section
  ```python
  updated_doc = replace_first_project_safely(doc, project_title, bullets)
  ```

### `utils/`

Helper utilities for validation and formatting:

- **`schema.py`**: JSON parsing & validation with `SchemaError` exceptions
  ```python
  payload = safe_load_json(llm_output)
  bullets, assumptions, missing = validate_bullets_payload(payload)
  ```

- **`bullets.py`**: Bullet normalization (truncation, line splitting, count validation)
  ```python
  normalized = normalize_bullets(raw_bullets, max_chars=160, max_bullets=3)
  ```

## 🛡️ Error Handling & Resilience

The system includes multiple fallback layers to ensure reliability:

### Layer 1: JSON Schema Validation
```
Catches malformed LLM responses
→ If valid JSON with required keys: proceed
→ If invalid: move to fallback
```

### Layer 2: Fallback Bullets
```
If JSON parsing fails: generate safe default bullets
Default: "Built an end-to-end resume editing workflow..."
"Implemented multi-agent pipeline with schema validation..."
```

### Layer 3: Bullet Normalization
```
• Truncate to character limits
• Ensure valid bullet count (2-3)
• Fix line breaks and formatting
```

### Layer 4: Streamlit Error UI
```
• Clear error messages for missing API keys
• Upload failure notifications
• API rate limit warnings
```

## 📦 Dependencies

```
streamlit>=1.32.0          # Web UI framework
python-docx>=1.1.0        # DOCX file operations
openai>=1.0.0             # OpenAI API client
anthropic>=0.25.0         # Anthropic Claude API client
```

## 🔐 Security & Best Practices

### API Keys
- Store API keys in Streamlit Secrets (`.streamlit/secrets.toml`)
- Never commit secrets to version control
- Use environment variables in production

### Data Privacy
- Resume text is sent to LLM APIs for processing
- No data is stored or cached (except Streamlit session state)
- Each user session is independent

### Rate Limiting
- Implement API call throttling for production use
- Monitor token usage to manage costs
- Consider caching for repeated requests

## 🚦 Development & Customization

### Why Custom Crew Implementation?

This branch uses a lightweight, custom orchestration framework rather than the official CrewAI library to:
- ✅ Maintain fine-grained control over agent behavior
- ✅ Reduce external dependencies
- ✅ Ensure predictable, transparent execution flow
- ✅ Allow easy customization of the agent system
- ✅ Minimize API overhead & latency



## 📈 Future Enhancements

- [ ] Support for multiple project replacement
- [ ] Batch resume processing for bulk updates
- [ ] Custom agent templates library
- [ ] Resume formatting templates
- [ ] Performance metrics & cost tracking
- [ ] ATS (Applicant Tracking System) optimization
- [ ] Multi-language support
- [ ] Real-time collaboration features
- [ ] Resume version history & comparison
- [ ] Export to PDF, LinkedIn, etc.

