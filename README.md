# External Business Intel

AI-backed backend and operator console for a private external business intelligence system.

This repository supports public-domain business intelligence workflows: trend scanning, source-bound ETL, governed AI analysis, stored reporting, and human-reviewed decision support.

## CV 1.1 Human-Centered Governance

This system does not treat AI as inherently dangerous. The risk comes from unbounded AI use inside uncontrolled workflows, especially when probabilistic output is treated as deterministic truth.

CV 1.1 exists to protect the people using AI by forcing the system to produce bounded, traceable, decision-support-grade outputs.

The model is not the decision-maker. The model is an input to a human decision process.

The system therefore enforces:

- defined scope
- controlled constraints
- evidence-bound output
- structured schemas
- fail-closed or deterministic fallback behavior
- human-in-the-loop review before operational action

Scope defines what an AI component is allowed to do. Constraint defines how that AI component is allowed to do it.

Applied to this system:

- DeepSeek remains a local ETL wrapper only.
- DeepSeek performs extraction, normalization, deduplication, and validation.
- DeepSeek does not interpret, recommend, or decide.
- Qwen is scoped as a tactical analyst only.
- Qwen analyzes normalized, source-bound, public-domain evidence.
- Qwen does not mutate, rewrite, normalize, extract, load, or delete records.
- Qwen must return structured outputs with evidence, confidence, score, implication, and recommended action.

## System Flow (Governed Execution)

```text
[ Public-Domain Sources ]
            ↓
[ Policy Validation Layer ]
 (blocks non-public / restricted data)
            ↓
[ Deterministic ETL (DeepSeek) ]
 (normalize → dedupe → validate → structure)
            ↓
[ Constrained Qwen Analysis ]
 (scoped role + evidence-bound output)
            ↓
[ Validation / Fallback Layer ]
 (reject invalid → fallback deterministic if needed)
            ↓
[ Neon Storage ]
 (structured, auditable records)
            ↓
[ UI / API Review Layer ]
 (Streamlit / endpoints)
            ↓
[ Human Decision (HITL) ]
 (approve / reject / act)
```

Current governed chain:

```text
public-domain data -> policy validation -> deterministic ETL -> constrained Qwen analysis -> Neon storage -> UI review -> human action
```

Full note: [CV 1.1 Human-Centered AI Governance](docs/cv11-human-centered-ai-governance.md)

## Backend stack

- FastAPI API service
- SQLAlchemy ORM
- Neon/PostgreSQL database via `DATABASE_URL`
- Qwen through Hugging Face Router via `HF_TOKEN`
- Local deterministic ETL wrapper
- Public-domain policy validation
- Streamlit operator console in `/ui`

## Core API workflow

1. Submit a public-domain trend query.
2. Ingest approved public sources.
3. Enforce public-source and prohibited-data policy.
4. Normalize, deduplicate, and validate records through the ETL layer.
5. Analyze source-bound records with Qwen or deterministic fallback.
6. Store the report in Neon.
7. Review output through API or UI before any human action.

## Key endpoints

```text
GET /health
GET /admin/smoke
GET /trends/scan?query=social%20media%20marketing
GET /trends/history
GET /trends/latest
```

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

## Required environment variables

```text
DATABASE_URL=postgresql://...
HF_TOKEN=hf_...
```

Optional:

```text
QWEN_MODEL=Qwen/Qwen3.6-35B-A3B:featherless-ai
QWEN_BASE_URL=https://router.huggingface.co/v1
```

## Status

Private operator system under active build. Current mode: public-domain ingestion, governed ETL, constrained Qwen analysis, Neon persistence, Streamlit UI hooks.
