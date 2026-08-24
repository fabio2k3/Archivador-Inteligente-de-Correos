# 📬 Casillero — Email Triage Agent

An intelligent email archiving service that reads your Gmail inbox, summarizes long emails into 3 concise bullet points, extracts invoice/payment due dates, classifies messages using a hybrid rules + AI system, and automatically moves unread newsletters older than 7 days into a "Pendientes" label — without ever deleting anything.

Built as an end-to-end learning project covering OAuth2, background job processing, hybrid AI/rule-based classification, and a full REST API with a custom dashboard.

## ✨ Features

- **Gmail integration** via OAuth2 — reads inbox metadata and applies labels without touching message content destructively
- **AI-powered summarization** — every email gets a 3-bullet summary and, when applicable, an extracted due date (e.g. from invoices)
- **Resilient AI fallback chain** — tries multiple free models (Qwen2.5-72B-Instruct → Llama-3.3-70B-Instruct → DeepSeek-V3) via the Hugging Face Inference API, so a single provider outage or quota limit doesn't break the pipeline
- **Hybrid classification** — deterministic rules catch obvious spam/newsletter patterns instantly and for free; the AI decides everything else
- **Automatic archiving** — newsletters unread for 7+ days are labeled "Pendientes" in Gmail (never deleted, never lost)
- **Fully automated** — a Celery Beat schedule syncs the inbox every 30 minutes with no manual intervention
- **Idempotent by design** — re-syncing never reprocesses an email twice, saving both time and AI quota
- **REST API** — list emails, filter by category, view pending items, and trigger a manual sync
- **Custom dashboard** — a distinctive "postal archive" themed UI to browse triaged correspondence visually
- **Structured logging + automated tests** — every service logs to console and file; core logic (classification, idempotency) is covered by a pytest suite with mocks

## 🏗️ Architecture

```
Gmail API  ──┐
             ├──▶  Email Orchestrator ──▶ PostgreSQL
Hugging Face ┘            │
                           ▼
                  Classification Service
                  (rules + AI hybrid)

Celery Beat ──▶ Redis (broker) ──▶ Celery Worker ──▶ (runs the orchestrator every 30 min)

FastAPI ──▶ REST API ──▶ Dashboard (static HTML/CSS/JS)
```

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI |
| Database | PostgreSQL + SQLAlchemy + Alembic (migrations) |
| Background jobs | Celery + Redis |
| AI | Hugging Face Inference API (Qwen2.5-72B, Llama-3.3-70B, DeepSeek-V3) |
| Email source | Gmail API (OAuth2) |
| Testing | pytest, unittest.mock, SQLite in-memory fixtures |
| Frontend | Vanilla HTML/CSS/JS, served via FastAPI static files |
| Containerization | Docker (Redis, and app image for deployment) |

## 📂 Project Structure

```
email-triage-agent/
├── app/
│   ├── main.py                  # FastAPI entrypoint
│   ├── core/
│   │   ├── config.py             # environment-based settings (Pydantic)
│   │   └── logging_config.py     # console + file logging setup
│   ├── db/
│   │   ├── session.py            # SQLAlchemy engine/session
│   │   └── models.py             # Email model + EmailCategory enum
│   ├── services/
│   │   ├── gmail_service.py      # OAuth2, label creation/application
│   │   ├── ai_service.py         # AI analysis with fallback chain
│   │   ├── classification_service.py  # hybrid rules + AI classification
│   │   ├── email_orchestrator.py # ties Gmail + AI + DB together (idempotent)
│   │   └── pending_mover_service.py   # 7-day stale newsletter logic
│   ├── tasks/
│   │   └── celery_tasks.py       # Celery app + periodic sync task
│   └── api/
│       ├── routes.py             # REST endpoints
│       └── schemas.py            # Pydantic response models
├── static/
│   └── index.html                # dashboard (Casillero UI)
├── tests/
│   ├── conftest.py               # in-memory DB fixture
│   ├── test_classification_service.py
│   └── test_email_orchestrator.py
├── alembic/                      # DB migrations
├── Dockerfile
├── requirements.txt
└── .env                          # not committed — see setup below
```

## ⚙️ Setup

### 1. Prerequisites

- Python 3.12+
- PostgreSQL running locally (or a connection string to one)
- Docker (for Redis)
- A Google Cloud project with the Gmail API enabled
- A free Hugging Face account with an API token

### 2. Clone and install

```bash
git clone https://github.com/fabio2k3/Archivador-Inteligente-de-Correos.git
cd Archivador-Inteligente-de-Correos/email-triage-agent
python -m venv venv
venv\Scripts\Activate.ps1        # Windows
# source venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
```

### 3. Environment variables

Create a `.env` file in the project root:

```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/email_triage_db
HUGGINGFACE_API_KEY=hf_your_key_here
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 4. Google Cloud / Gmail API setup

1. Create a project at [console.cloud.google.com](https://console.cloud.google.com)
2. Enable the **Gmail API**
3. Configure the OAuth consent screen (add scopes: `gmail.readonly`, `gmail.labels`, `gmail.modify`)
4. Create OAuth credentials (type: **Desktop app**) and download as `credentials.json` into the project root
5. Run any script that calls `get_gmail_service()` once to complete the interactive login and generate `token.json`

> ⚠️ While the app is in "Testing" publishing status, Google expires the refresh token every 7 days. See [Future Improvements](#-future-improvements) below.

### 5. Database

```bash
docker run -d --name redis-email-triage -p 6379:6379 redis:7-alpine
alembic upgrade head
```

### 6. Run it

Open three terminals:

```bash
# Terminal 1 — API
uvicorn app.main:app --reload

# Terminal 2 — Celery worker
celery -A app.tasks.celery_tasks worker --loglevel=info --pool=solo   # remove --pool=solo on Linux/macOS

# Terminal 3 — Celery beat (scheduler)
celery -A app.tasks.celery_tasks beat --loglevel=info
```

Visit `http://127.0.0.1:8000` for the dashboard, or `http://127.0.0.1:8000/docs` for the interactive API docs.

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Tests cover the hybrid classification logic and the orchestrator's idempotency guarantee, using an in-memory SQLite database and mocked AI calls — no external services required.

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/emails` | List processed emails, optionally filtered by `category` |
| `GET` | `/api/emails/pending` | List emails moved to the Pendientes label |
| `GET` | `/api/emails/{id}` | Get a single email's detail |
| `POST` | `/api/sync/trigger` | Queue a manual sync (non-blocking, via Celery) |

## 🚀 Future Improvements

This project is fully functional as-is — the points below are planned enhancements, not blockers:

- **Publish the Google Cloud app to Production status.** Currently in "Testing" mode, which caps refresh tokens at 7 days, requiring periodic manual re-authentication. Moving to Production removes this limit entirely.
- **Deploy to a real server.** Currently runs locally; the next step is hosting the API, worker, and scheduler on a managed platform (e.g. Railway) with managed PostgreSQL and Redis, so the service runs unattended 24/7.
- **Add authentication to the API.** The REST API is currently open with no auth layer — adding an API key or token-based auth is needed before exposing it beyond local/personal use.

## 📄 License

Personal learning project — feel free to fork and adapt.
