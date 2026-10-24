from __future__ import annotations

import json
from pathlib import Path
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from regimpact.analysis import analyze
from regimpact.documents import extract_document, parse_clauses
from regimpact.models import BusinessProfile
from regimpact.store import get_report, recent_reports, save_report

ROOT = Path(__file__).parents[1]
SAMPLE_ROOT = ROOT / "sample_data"
DEMO_PROFILES = {
    "01_food_safety": {"name": "Acme Foods Pvt Ltd", "industry": "food processing", "state": "Karnataka", "employee_count": 42, "annual_turnover_lakh": 180, "activities": "food operator", "registrations": "FSSAI"},
    "02_labour_threshold": {"name": "Fabrix Garments", "industry": "garment manufacturing", "state": "Karnataka", "employee_count": 42, "annual_turnover_lakh": 95, "activities": "factory operations", "registrations": "Factory licence"},
    "03_ecommerce_scope": {"name": "Oak & Co", "industry": "furniture manufacturing", "state": "Karnataka", "employee_count": 18, "annual_turnover_lakh": 120, "activities": "B2B wholesale", "registrations": "GST"},
}

app = FastAPI(title="Regulatory Change Impact API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def profile_from_json(raw: str) -> BusinessProfile:
    try:
        return BusinessProfile.model_validate_json(raw)
    except ValidationError as exc:
        raise HTTPException(422, detail=json.loads(exc.json())) from exc

async def clauses_from_upload(upload: UploadFile):
    if not upload.filename or Path(upload.filename).suffix.lower() not in {".pdf", ".txt"}:
        raise HTTPException(422, detail="Upload a PDF or UTF-8 text document.")
    try:
        _, pages = extract_document(upload.filename, await upload.read())
        clauses = parse_clauses(pages)
    except Exception as exc:
        raise HTTPException(422, detail=f"Could not read {upload.filename}: {exc}") from exc
    if not clauses:
        raise HTTPException(422, detail=f"No readable text found in {upload.filename}.")
    return clauses

def run_analysis(profile: BusinessProfile, old_clauses, new_clauses) -> dict:
    report = analyze(old_clauses, new_clauses, profile)
    report_id = save_report(profile, report)
    return {"id": report_id, "report": report.model_dump()}

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/analyses")
async def create_analysis(profile: str = Form(...), earlier: UploadFile = File(...), updated: UploadFile = File(...)):
    business = profile_from_json(profile)
    return run_analysis(business, await clauses_from_upload(earlier), await clauses_from_upload(updated))

@app.get("/api/reports")
def list_reports():
    return recent_reports()

@app.get("/api/reports/{report_id}")
def retrieve_report(report_id: int):
    report = get_report(report_id)
    if not report:
        raise HTTPException(404, detail="Report not found.")
    return report

@app.get("/api/demos")
def demos():
    return [{"id": scenario, "title": title, "expected": expected, "profile": profile} for scenario, title, expected, profile in [
        ("01_food_safety", "Food safety digital register", "Likely applies", DEMO_PROFILES["01_food_safety"]),
        ("02_labour_threshold", "Employment threshold update", "Possibly applies", DEMO_PROFILES["02_labour_threshold"]),
        ("03_ecommerce_scope", "Marketplace disclosure scope", "Needs review", DEMO_PROFILES["03_ecommerce_scope"]),
    ]]

@app.post("/api/demos/{scenario_id}/analyses")
def run_demo(scenario_id: str):
    profile_data = DEMO_PROFILES.get(scenario_id)
    folder = SAMPLE_ROOT / scenario_id
    if not profile_data or not folder.is_dir():
        raise HTTPException(404, detail="Demo scenario not found.")
    old_file, new_file = folder / "earlier.pdf", folder / "updated.pdf"
    try:
        _, old_pages = extract_document(old_file.name, old_file.read_bytes())
        _, new_pages = extract_document(new_file.name, new_file.read_bytes())
    except Exception as exc:
        raise HTTPException(500, detail=f"Demo files could not be read: {exc}") from exc
    return run_analysis(BusinessProfile.model_validate(profile_data), parse_clauses(old_pages), parse_clauses(new_pages))
