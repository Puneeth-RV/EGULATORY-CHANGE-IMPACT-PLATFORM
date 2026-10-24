# RegImpact — Regulatory Change Impact Platform

An evidence-backed local web application for Indian SMEs. Compare regulatory documents, assess impact against a business profile, identify actions/deadlines, and retain a local report history.

## Run the judge demo

Open two terminals from the repository root.

```bash
# Terminal 1 — API
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

```bash
# Terminal 2 — web app
cd frontend
npm install
npm run dev
```

Open the address printed by Vite (normally `http://localhost:5173`). The frontend proxies `/api` requests to FastAPI at port 8000.

## Judge scenarios

Use the **Judge-ready demonstrations** cards in the web app. They use the checked-in paired source PDFs in `sample_data/`.

| Scenario | Expected result |
| --- | --- |
| Food safety digital register | Likely applies |
| Employment threshold update | Possibly applies |
| Marketplace disclosure scope | Needs review |

You can also upload any text-based PDF or `.txt` pair. The product retains clause/page evidence and saves the report locally in SQLite (`data/regimpact.db`).

## Test

```bash
.venv/bin/python -m pytest -q
cd frontend && npm test
```

## Design boundaries

The visible workflow is deterministic and evidence-first; no AI toggle is shown. This is an operational aid, not legal advice. Scanned-PDF OCR, authentication, and hosted multi-user storage are intentionally out of scope for the hackathon MVP.
