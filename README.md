# AIVOA Complaint Management System

AI-assisted customer complaint intake for pharmaceutical API and FDF quality assurance workflows.

## Overview

This project is a focused single-page Complaint Management experience. It combines a structured Complaint Log with an AIVOA Copilot that can interpret complaint text, extract complaint data, update the form, and provide an initial risk assessment.

The current codebase includes the completed UI milestone, a FastAPI intake endpoint, and an optional LangGraph/Groq extraction path that falls back to deterministic demo extraction when no API key is configured.

## Core features

- Complaint Log with origin, customer, product, batch, complaint category, and complaint details
- Data-driven, reusable complaint sections and field components
- AIVOA Copilot with persistent right-side desktop layout and mobile overlay drawer
- Copilot collapse/expand state persisted locally
- Independent complaint-form and Copilot chat scrolling
- Chat composer that remains visible while chat history scrolls
- Natural-language demo extraction and complaint edits
- PDF, DOCX, TXT, and EML upload affordances with drag-and-drop support
- Source-file attribution for extracted results
- AI-populated field success highlighting
- DD/MM/YYYY date entry and calendar picker controls
- Form-only reset behavior that preserves conversation history
- Explicit new-chat confirmation before clearing conversation history
- FastAPI intake endpoint with optional LangGraph/Groq extraction and local demo fallback
- Local SQLite persistence with duplicate-save protection and a Saved Complaints viewer

## Architecture

```text
src/
  components/complaint/       Reusable Complaint Log UI components
  features/complaint/         Complaint configuration and date utilities
  services/                   Frontend API client
  App.jsx                     Single-page composition and Copilot workflow
  store.js                    Redux complaint state
  styles.css                  UI styling and responsive layout

backend/
  app/main.py                 FastAPI application and routes
  app/schemas.py              API request/response models
  app/services/               Extraction service boundary, demo, date, document, and LangGraph implementations
  app/database.py             SQLAlchemy engine and local schema setup
  app/models.py               Portable complaint persistence model
  tests/                      Extraction regression tests
  requirements.txt            Backend dependencies
  .env.example                Backend configuration template
```

The UI is modular so the demo extractor can be replaced by a LangGraph workflow without coupling AI logic to presentation components.

## AI Model Selection

### Original Plan

The project was initially evaluated with the intention of using the following models:

- `gemma2-9b-it`
- `llama-3.3-70b-versatile`

### Implementation Outcome

During implementation and environment setup, the originally planned models were not available or suitable for the project's deployment environment and access tier. To avoid blocking development and ensure a stable AI integration, the project was migrated to:

`openai/gpt-oss-20b`

### Current AI Model

The Complaint Management Co-Pilot and AI extraction workflows now use:

`openai/gpt-oss-20b`

Reasons:

- Available and supported in the deployment environment.
- Supports long-context processing with a 131K context window.
- Supports tool usage and agentic workflows.
- Supports structured outputs and function calling.
- Suitable for document analysis and complaint data extraction workflows.

### Future Flexibility

The system has been designed to remain model-agnostic wherever possible. Future upgrades or migrations to newer supported models should require configuration changes rather than major architectural changes.

### Important Note

- `gemma2-9b-it` is not the active model.
- `llama-3.3-70b-versatile` is not the active model.
- `openai/gpt-oss-20b` is the current production model used by the project.

## Prerequisites

- Node.js 18 or newer
- npm
- Python 3.11 or newer
- Docker Desktop (optional, for local PostgreSQL)
- A Groq account and API key for the real AI integration phase

## Installation

```powershell
npm install

python -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
```

## Local development

Start the frontend:

```powershell
npm run dev
```

Open `http://localhost:5173`.

Start the backend in a second terminal:

```powershell
backend\.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --reload --port 8000
```

Verify the backend at `http://localhost:8000/api/health`.

The frontend calls FastAPI when available and falls back to the local demo extractor when it is not.

## Environment configuration

```powershell
Copy-Item backend\.env.example backend\.env
```

For local development with SQLite and real Groq/LangGraph processing, set:

```env
GROQ_API_KEY=your_groq_key
GROQ_MODEL=openai/gpt-oss-20b
DATABASE_URL=sqlite:///./backend/ccms.sqlite3
CORS_ORIGINS=http://localhost:5173
```

Never place API keys in frontend files or commit `.env` files.

## PostgreSQL

```powershell
docker compose up -d postgres
```

The SQLAlchemy persistence model is PostgreSQL-ready. After PostgreSQL is running, replace `DATABASE_URL` in `backend\.env` with:

```env
DATABASE_URL=postgresql+psycopg://ccms:ccms@localhost:5432/ccms
```

Restart FastAPI and it will create the same `complaint_records` table in PostgreSQL. SQLite remains the default local database so PostgreSQL is not required for frontend development.

## Build and verification

```powershell
npm run build
python -m compileall -q backend
```

## Deployment

Build the frontend with `npm run build` and serve `dist/` from a static host or reverse proxy. Run FastAPI with a production ASGI process, configure managed PostgreSQL, store secrets in the deployment platform's secret manager, and restrict CORS to the deployed frontend origin.

## Roadmap

Completed:

- Single-page Complaint Log UI
- Responsive AIVOA Copilot experience
- Redux complaint state
- FastAPI intake endpoint
- Optional LangGraph/Groq extraction path
- Modular frontend and backend boundaries

Next:

- Add document parsing service
- Migrate local SQLite records to PostgreSQL when hosting begins
- Add complaint history and audit events
- Add authentication and role-based access
- Add reporting, duplicate detection, CAPA suggestions, and completeness checks

## Contribution guidelines

1. Create a focused feature branch from `main`.
2. Keep UI, API, and extraction logic separated.
3. Use Conventional Commit messages such as `feat(ui): ...` or `fix(api): ...`.
4. Run the build and backend checks before opening a pull request.
5. Never commit secrets, environment files, generated artifacts, or local databases.

## License

This project is currently an assignment/demo repository. Add a formal license before public redistribution.
