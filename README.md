# RegImpact

> Evidence-backed regulatory change review for Indian SMEs.

RegImpact compares two regulatory-document versions, identifies clause-level changes, evaluates those changes against a saved business profile, and produces practical action tasks with source evidence.

It answers three questions: **What changed? Does it affect this business? What should happen next, and by when?**

![Status](https://img.shields.io/badge/status-hackathon%20MVP-244f92) ![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB) ![Frontend](https://img.shields.io/badge/frontend-React%20%2B%20Vite-61DAFB)

## What works today

- Upload and compare text-based PDF or UTF-8 text document versions.
- Preserve clause identifiers, source text, old/new page references, and comparison confidence.
- Apply explicit, checked-in rules for the synthetic judge scenarios.
- Return **Applies**, **Does not apply**, or **Needs verification**—never a guessed conclusion for an unconfigured regulation.
- Save/reuse business profiles; unknown fields remain unknown rather than becoming a negative answer.
- Save local SQLite report history and update action status: Not started, In progress, Completed, or Needs review.
- Run one-click judge demos with checked-in sample documents.

## Quick start

### Prerequisites

- Python 3.11+
- Node.js 20+

### Install

```bash
git clone https://github.com/Puneeth-RV/EGULATORY-CHANGE-IMPACT-PLATFORM.git
cd EGULATORY-CHANGE-IMPACT-PLATFORM

python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cd frontend && npm install && cd ..
```

### Run

Use two terminals from the repository root.

```bash
# Terminal 1 — FastAPI backend
source .venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

```bash
# Terminal 2 — React frontend
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Vite proxies `/api` to `http://127.0.0.1:8000`.

### Verify

```bash
.venv/bin/python -m pytest -q
cd frontend && npm test && npm run build
```

## Judge demo script

Use the cards under **Judge-ready demonstrations**. They use clearly labelled synthetic fixtures in [`sample_data/`](sample_data/README.md), not live legal sources.

| Scenario | Profile signal | Expected outcome | What it proves |
| --- | --- | --- | --- |
| Food safety digital register | Activity: food operator | **Applies** | Clause change, source-backed rule, supported deadline, task tracking |
| Employment threshold update | 42 employees | **Applies** | Deterministic threshold rule |
| Marketplace disclosure scope | B2B furniture wholesale | **Does not apply** | No false task when a rule condition is unmet |

Suggested presentation sequence:

1. Save the prefilled food business profile.
2. Run **Food safety digital register**.
3. Expand Rule 4 to show old/new text, source pages, confidence, and evidence.
4. Highlight the rule rationale, supported deadline, and task status control.
5. Open History to show local persistence.
6. Run the employment scenario; clear employee count to explain **Needs verification** for missing evidence.
7. Run the marketplace scenario to show **Does not apply**.

## Architecture

```text
React + Vite dashboard
        │ /api
        ▼
FastAPI modular monolith
        ├── PyMuPDF extraction + clause parsing
        ├── deterministic change detector
        ├── explicit JSON rule evaluator
        ├── evidence/action report builder
        └── SQLite persistence
```

| Directory | Responsibility |
| --- | --- |
| `backend/` | HTTP endpoints for analysis, profiles, reports, demos, and task status |
| `regimpact/` | Reusable document, comparison, rule, model, and storage logic |
| `rules/` | Rules separate from UI code; current rules support only synthetic fixtures |
| `frontend/` | React compliance workspace |
| `sample_data/` | Repeatable synthetic PDF/text demo pairs |
| `tests/` | Unit and HTTP workflow coverage |

## API summary

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Health check |
| `POST` | `/api/analyses` | Analyze multipart `earlier`, `updated`, and `profile` data |
| `GET/POST` | `/api/profiles` | Reuse local business profiles |
| `GET` | `/api/reports` | Recent local analyses |
| `GET` | `/api/reports/{id}` | Reopen a report |
| `PATCH` | `/api/actions/{id}` | Update persisted task status |
| `GET` | `/api/demos` | List synthetic scenarios |
| `POST` | `/api/demos/{id}/analyses` | Run a synthetic scenario |

## Data and safeguards

- Data remains local in `data/regimpact.db`; set `REGIMPACT_DB_PATH` to use another local SQLite location.
- Uploaded files are untrusted input. Only `.pdf` and `.txt` are accepted; files are limited to 10 MB.
- Empty and encrypted PDFs are rejected with actionable errors.
- Deterministic comparisons and configured rules are authoritative. No AI model currently decides applicability, citations, deadlines, or actions.

## Known limitations

- Text-based PDFs only; scanned documents require OCR, which is not included.
- Rules are configured only for synthetic demo fixtures. Other documents correctly return **Needs verification** until a verified rule is added.
- Clause alignment is identifier-based; complex renumbering/reordered clauses need further matching work.
- This is a local single-user MVP: no authentication, cloud storage, or collaboration.
- Reports are JSON-downloadable. Printable HTML/Markdown/PDF export is future work.

## Legal disclaimer

**This application provides regulatory information and compliance assistance, not definitive legal advice. Verify important obligations against official sources or with a qualified professional.**
