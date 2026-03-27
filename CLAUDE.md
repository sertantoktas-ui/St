# CLAUDE.md — AI Assistant Guide

This file provides context for AI assistants (Claude Code and others) working on this codebase.

---

## Project Overview

A Python-based personal assistant application powered by the Claude API. The project demonstrates three complexity tiers of AI assistant implementation, from a minimal chat client to a full agentic system with tool use, database persistence, email sending, and PDF generation. Documentation and user-facing text are primarily in Turkish.

---

## Repository Structure

```
St/
├── full_featured_assistant.py   # Primary app: full tool use + database + email + PDF
├── advanced_assistant.py        # Intermediate: tool use, in-memory only
├── personal_assistant.py        # Basic: chat-only, no tools
├── database.py                  # SQLite persistence layer
├── email_service.py             # SMTP email service (Gmail/Outlook/custom)
├── pdf_generator.py             # PDF report generation (ReportLab)
├── streamlit_app.py             # Streamlit web UI
├── requirements.txt             # Python dependencies
├── .env.example                 # Required environment variables template
├── .streamlit/config.toml       # Streamlit theme and server config
├── Procfile                     # Heroku/Railway process declaration
├── railway.toml                 # Railway.app deployment config
├── PersonalAssistant.spec       # PyInstaller config for Windows EXE build
├── README.md                    # Project overview (Turkish)
├── SETUP.md                     # Installation guide (Turkish)
├── DEPLOY.md                    # Deployment guide (Turkish)
└── STREAMLIT_KURULUM.md         # Streamlit setup guide (Turkish)
```

---

## Architecture

The application follows a layered architecture:

```
UI Layer          → CLI (assistant scripts) or Streamlit web UI
AI Layer          → Anthropic SDK + Tool Use / agentic loop
Business Logic    → full_featured_assistant.py, advanced_assistant.py, personal_assistant.py
Service Layer     → database.py, email_service.py, pdf_generator.py
```

### Application Tiers

| File | Complexity | Persistence | Tools | Use Case |
|------|-----------|-------------|-------|----------|
| `personal_assistant.py` | Basic | None | None | API testing, simple chat |
| `advanced_assistant.py` | Intermediate | In-memory | 4 tools | Tool use learning |
| `full_featured_assistant.py` | Full | SQLite | 4 tools | Production use |

---

## Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `anthropic` | >=0.30.0 | Claude API client (core dependency) |
| `python-dotenv` | >=1.0.0 | Loads `.env` configuration |
| `reportlab` | >=4.0.0 | PDF generation |
| `weasyprint` | >=60.0 | HTML-to-PDF fallback |
| `streamlit` | >=1.28.0 | Web UI |
| `requests` | >=2.31.0 | HTTP client |

**Model in use:** `claude-opus-4-6`

---

## Development Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY at minimum

# 4. Run desired tier
python personal_assistant.py        # Basic chat
python advanced_assistant.py        # Tool use demo
python full_featured_assistant.py   # Full featured CLI
streamlit run streamlit_app.py      # Web UI
```

---

## Environment Variables

Defined in `.env` (copy from `.env.example`):

```env
# Required
ANTHROPIC_API_KEY=your-api-key-here

# Optional user config
USER_NAME=YourName
USER_EMAIL=user@example.com

# Optional email (SMTP) config
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password-here
```

The application checks for `email_available` at runtime — missing SMTP config disables email features gracefully.

---

## Tool Use Pattern (Claude Agentic Loop)

`full_featured_assistant.py` and `advanced_assistant.py` implement Claude's tool use pattern:

1. Define tools with JSON schemas (name, description, input_schema)
2. Send user message + tool definitions to Claude API
3. Check `stop_reason == "tool_use"` in the response
4. Execute the requested tool function(s)
5. Append `tool_result` content blocks to conversation history
6. Call Claude API again to get the final response
7. Repeat until `stop_reason == "end_turn"`

**Defined tools:**
- `create_email` — Draft and optionally send an email via SMTP
- `create_report` — Generate and save a PDF report
- `manage_task` — Add, list, or complete tasks (stored in SQLite)
- `get_statistics` — Return aggregated counts from the database

---

## Database Schema (`database.py`)

SQLite database stored at `./assistant.db` (auto-created on first run).

| Table | Key Columns |
|-------|-------------|
| `tasks` | id, title, description, status, priority, created_at, completed_at |
| `emails` | id, recipient, subject, body, tone, sent, created_at |
| `reports` | id, title, content, format, file_path, created_at |
| `search_history` | id, query, created_at |

Test database operations directly: `python database.py`

---

## Service Modules

### `email_service.py`
- Supports Gmail, Outlook, or custom SMTP
- Key methods: `send_email()`, `send_bulk_emails()`, `create_professional_email()`, `create_html_email()`
- Test: `python email_service.py`

### `pdf_generator.py`
- Output directory: `./reports/`
- Generators: `generate_from_text()`, `generate_from_markdown()`, `generate_invoice_style()`
- Test: `python pdf_generator.py`

---

## Code Conventions

- **Classes:** CamelCase (`DatabaseManager`, `EmailService`)
- **Functions/variables:** snake_case (`get_statistics`, `send_email`)
- **User-facing text:** Turkish with emoji prefixes (`✅ Görev tamamlandı`, `❌ Hata`)
- **Error handling:** Try/except with graceful fallbacks; optional features degrade silently
- **Type hints:** Used in service modules (`Dict`, `List`, `Optional`)
- **Docstrings:** Present on public methods in service modules
- **No test framework:** Module-level `__main__` blocks and standalone test functions

---

## Testing

There is no pytest/unittest suite. Each module has manual test blocks:

```bash
python database.py          # Tests CRUD and statistics
python email_service.py     # Tests email initialization and templates
python pdf_generator.py     # Tests PDF generation (creates files in ./reports/)
```

When modifying a module, run its corresponding test block to verify functionality.

---

## Deployment

### Railway.app
- Configured via `railway.toml` (nixpacks builder)
- Start command: `streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0`
- Set `ANTHROPIC_API_KEY` and optional SMTP vars as Railway secrets

### Streamlit Cloud
- Connect GitHub repo, set secrets in dashboard
- Entry point: `streamlit_app.py`

### Windows EXE
- Build with: `pyinstaller PersonalAssistant.spec`
- Output: `dist/PersonalAssistant.exe`
- Bundles `full_featured_assistant.py` with `anthropic` hidden import

---

## Git Workflow

- **Active development branch:** `claude/add-claude-documentation-XkVXo`
- **Main branch:** `main`
- Commit messages follow imperative style in English or Turkish
- Push with: `git push -u origin <branch-name>`

---

## Important Notes for AI Assistants

1. **Documentation is in Turkish** — user-facing strings, README, SETUP, and DEPLOY docs are Turkish. Do not change the language of existing user-facing text unless asked.
2. **Three tiers exist for a reason** — `personal_assistant.py` is intentionally minimal. Do not add tool use or database features to it.
3. **No test framework** — add tests as `__main__` blocks or standalone functions, not pytest, unless explicitly asked.
4. **SMTP is optional** — email features must remain gracefully degradable when SMTP env vars are absent.
5. **Model pinned to `claude-opus-4-6`** — do not change the model string without explicit instruction.
6. **`assistant.db` is gitignored** — never commit the SQLite database file.
7. **`reports/` directory** — PDF output files go here; directory is created at runtime if absent.
8. **`build/` and `dist/` are gitignored** — PyInstaller output should not be committed.
