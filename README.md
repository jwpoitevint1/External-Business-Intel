# External Business Intel

AI-backed backend for a local marketing-operations business system.

This repository is structured to support external business intelligence workflows: prospect discovery, business profile audits, outreach scripting, sprint-based delivery, indicator-code tracking, CRM-style lead management, and human-approved AI assistance.

## Backend stack

- FastAPI API service
- SQLAlchemy ORM
- SQLite by default for local development
- Pydantic settings and schemas
- Modular services for AI-assisted audits and outreach drafting
- Human approval gates for external-facing actions

## Core workflow

1. Add a prospect/business profile.
2. Run an AI-assisted public-presence audit.
3. Generate a visibility score and recommended fixes.
4. Draft outreach or review-pivot messages.
5. Require human approval before any external action.
6. Track indicator codes, lead status, sprint activity, and measurable response.

## Local start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Status

Initial backend scaffold. Not production-hardened yet.
