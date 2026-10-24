# Regulatory Change Impact Platform

An evidence-backed Streamlit MVP for Indian SMEs. Upload an earlier and updated regulatory document (PDF or text), enter a business profile, and receive deterministic clause-level changes, a profile-specific applicability signal, action items, deadlines, source evidence, and saved report history.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

Run checks with `pytest -q`.

## Demo workflow

1. Enter the SME profile in the sidebar (try `food processing`, activity `food operator`).
2. Upload two `.txt` or text-based PDF versions. Use headings such as `Rule 4 Registration` for the strongest clause matching.
3. Click **Analyze change impact**. Inspect evidence expanders for original text and page references.
4. Review action/deadline table and download the JSON report. Reports are persisted in `data/regimpact.db`.

## AI and reliability

The core workflow is deliberately deterministic and works without an API key. `GEMINI_API_KEY` is reserved for an optional interpretation layer; the application never relies on generative output to identify source evidence or make the workflow available. For production, add authenticated users, source-version hashing, OCR for scanned PDFs, legal-review queues, and a Gemini structured-output adapter validated against the included Pydantic models.
