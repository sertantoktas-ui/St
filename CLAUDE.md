# CLAUDE.md

This file provides guidance for AI assistants working on the **Claude AI Kişisel Asistan** (Claude AI Personal Assistant) project.

## Project Overview

A Turkish-language personal assistant framework built on Claude Opus 4.6, with three complexity tiers, a Streamlit web UI, and a specialized technical service management system. All documentation, UI, and user-facing strings are in Turkish.

## Repository Structure

```
St/
├── personal_assistant.py        # Tier 1: Simple conversation-only assistant
├── advanced_assistant.py        # Tier 2: Conversation + Claude Tool Use (in-memory)
├── full_featured_assistant.py   # Tier 3: Full stack (DB + email + PDF + tools)
├── streamlit_app.py             # Web UI (4 tabs: Chat, Notes, Email, PDF)
├── teknik_servis_app.py         # Standalone Technical Service Management Streamlit app
├── teknik_servis_db.py          # Database layer for technical service system
├── database.py                  # SQLite ORM for the main assistant
├── email_service.py             # SMTP email abstraction (Gmail/Outlook)
├── pdf_generator.py             # PDF generation via ReportLab
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
├── railway.toml                 # Railway.app deployment config
├── Procfile                     # Process definition (Streamlit on $PORT)
├── PersonalAssistant.spec       # PyInstaller spec for standalone executable
├── .streamlit/config.toml       # Streamlit theme and server settings
└── dist/                        # Pre-built binaries (do not edit)
```

## Architecture

### Three-Tier Assistant Design

The three assistant Python files represent a progressive enhancement pattern — each builds on concepts from the previous:

| File | DB | Tools | Email | PDF |
|---|---|---|---|---|
| `personal_assistant.py` | No | No | No | No |
| `advanced_assistant.py` | No | Yes (in-memory) | No | No |
| `full_featured_assistant.py` | Yes | Yes | Yes | Yes |

- The Streamlit UI (`streamlit_app.py`) integrates with the full-featured tier.
- The technical service system (`teknik_servis_app.py`) is a standalone Streamlit application with its own DB layer.

### Claude Tool Use (Agentic Loop)

`advanced_assistant.py` and `full_featured_assistant.py` implement the standard Claude Tool Use pattern:
1. Tools are defined as JSON schemas and passed to `client.messages.create(tools=[...])`
2. When Claude returns `stop_reason == "tool_use"`, extract tool calls from `response.content`
3. Execute tools locally and format results as `tool_result` messages
4. Append both the assistant response and tool results to the message history
5. Call the API again — continue until `stop_reason == "end_turn"`

Always use `claude-opus-4-6` as the model ID (not the older alias format).

### Database Schema

**`database.py` — AssistantDatabase (SQLite: `assistant.db`)**

| Table | Key Fields |
|---|---|
| `tasks` | id, title, description, status (pending/completed), priority (low/medium/high), created_at, completed_at |
| `emails` | id, recipient, subject, body, tone, created_at, sent_at, sent (0/1) |
| `reports` | id, title, content, format, created_at, file_path |
| `search_history` | id, query, results, created_at |

**`teknik_servis_db.py` — TeknikServisDB (SQLite: `teknik_servis.db`)**

| Table | Key Fields |
|---|---|
| `musteriler` | id, ad, soyad, telefon, email, adres |
| `cihazlar` | id, musteri_id (FK), marka, model, seri_no, cihaz_tipi, satin_alma_tarihi, notlar |
| `is_emirleri` | id, cihaz_id (FK), ariza_aciklama, durum, teknisyen, oncelik, baslangic_tarihi, bitis_tarihi |
| `parcalar` | id, is_emri_id (FK), parca_adi, miktar, birim_fiyat |
| `faturalar` | id, is_emri_id (FK), toplam_tutar, odeme_durumu, fatura_tarihi |

Work order statuses (`durum`): `Beklemede` / `Devam Ediyor` / `Tamamlandı` / `Teslim Edildi`

## Development Workflow

### Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY
```

### Running Locally

```bash
# Terminal-based assistants
python personal_assistant.py
python advanced_assistant.py
python full_featured_assistant.py

# Web UI (main assistant)
streamlit run streamlit_app.py

# Web UI (technical service)
streamlit run teknik_servis_app.py
```

Streamlit runs on port **8501** by default.

### Environment Variables

**Required:**
- `ANTHROPIC_API_KEY` — Claude API key (`sk-ant-...` format from console.anthropic.com)

**Optional (email features):**
- `SMTP_SERVER` — Default: `smtp.gmail.com`
- `SMTP_PORT` — Default: `587`
- `SENDER_EMAIL` — Sender email address
- `SENDER_PASSWORD` — App password (for Gmail: generate at myaccount.google.com/apppasswords)

**Optional (user info):**
- `USER_NAME`
- `USER_EMAIL`

Never hardcode credentials. Always use `python-dotenv` to load from `.env`.

## Key Conventions

### Language

All user-facing strings, UI labels, error messages, docstrings, and database field names are in **Turkish**. AI-generated content (emails, reports) is also in Turkish. Code identifiers (variables, functions, classes) use English or Turkish depending on context — follow the existing style in the file being modified.

### Claude API Usage

- Model: `claude-opus-4-6` (always use this exact string)
- Always pass a `system` prompt that sets context for the assistant's role
- Keep conversation history as a list of `{"role": ..., "content": ...}` dicts
- `max_tokens` is typically set to `4096` for tool use and `2048` for simple chat

### PDF Generation

- Output directory: `./reports/` (auto-created by `PDFReportGenerator.__init__`)
- Uses ReportLab `SimpleDocTemplate` with A4 page size
- Primary heading color: `#2E5090`
- Always include metadata (title, author from `USER_NAME`, date)

### Email Service

- Default SMTP: Gmail on port 587 with STARTTLS
- For Gmail, users must use an App Password, not their account password
- HTML emails use the `create_html_email()` template method
- Tone options: `formal` / `casual` / `friendly`

### Streamlit UI

- Theme configured in `.streamlit/config.toml`: dark mode, primary color `#FF6B6B`
- Tab structure must remain: 💬 Sohbet | 📝 Notlar | 📧 Email | 📄 PDF
- Use `st.session_state` for all stateful data (chat history, etc.)
- Max upload size: 200MB

## Deployment

### Railway.app (Primary)

Configured via `railway.toml`:
- Builder: nixpacks (auto-detects Python)
- Start command: `streamlit run streamlit_app.py`
- Health checks enabled on port 8501
- Set `ANTHROPIC_API_KEY` in Railway environment variables dashboard

### Streamlit Cloud (Alternative)

- Connects to GitHub repo directly
- Secrets set via the Streamlit Cloud dashboard (mirrors `.env` format)
- Every push to the target branch triggers a redeploy

### Standalone Executable

Build with PyInstaller using the spec file:
```bash
pyinstaller PersonalAssistant.spec
```
Output lands in `dist/`. The spec hides `anthropic` imports and runs in non-console mode.

## Important Notes for AI Assistants

1. **Do not modify `dist/`** — pre-built binaries, not source code.
2. **SQLite databases (`*.db`) are excluded from git** via `.gitignore`. Never commit them.
3. **The three assistant files have intentional duplication** — they are standalone examples at different complexity levels. Do not refactor shared logic into a common module without explicit instruction, as this breaks the educational/demo purpose.
4. **Documentation is in Turkish** — README.md, SETUP.md, DEPLOY.md, STREAMLIT_KURULUM.md. Keep any new documentation consistent with the existing language.
5. **Tool schemas in advanced/full-featured assistants must stay in sync** if the same tool is defined in both files.
6. **`teknik_servis_app.py` and `teknik_servis_db.py` are a self-contained subsystem** — they do not import from `database.py`, `email_service.py`, or `pdf_generator.py`.
