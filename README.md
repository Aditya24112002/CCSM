# AIVOA Complaint Management System

AI-assisted customer complaint intake for pharmaceutical API and FDF quality assurance workflows.

## Overview

This project is a focused single-page Complaint Management experience. It combines a structured Complaint Log with an AIVOA Copilot that can interpret complaint text, extract complaint data, update the form, and provide an initial risk assessment.

The current release completes the UI milestone and includes a local FastAPI demo endpoint ready for the next backend integration phase.

## Core features

- Complaint Log with origin, customer, product, batch, complaint, severity, and priority fields
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
- FastAPI intake endpoint with a local demo extraction fallback

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
  app/services/               Extraction service boundary and demo implementation
  requirements.txt            Backend dependencies
  .env.example                Backend configuration template
```

The UI is modular so the demo extractor can be replaced by a LangGraph workflow without coupling AI logic to presentation components.

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

For real Groq/LangGraph processing, set:

```env
GROQ_API_KEY=your_groq_key
DATABASE_URL=postgresql+psycopg://ccms:ccms@localhost:5432/ccms
CORS_ORIGINS=http://localhost:5173
```

Never place API keys in frontend files or commit `.env` files.

## PostgreSQL

```powershell
docker compose up -d postgres
```

The database configuration is local-first and can later be replaced with a managed PostgreSQL service.

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
- Demo FastAPI intake endpoint
- Modular frontend and backend boundaries

Next:

- Connect LangGraph orchestration
- Add real Groq extraction and risk assessment
- Add document parsing service
- Persist complaints in PostgreSQL
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
