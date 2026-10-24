from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
profile = '{"name":"Acme Foods","industry":"food processing","activities":"food operator","registrations":"FSSAI"}'

def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}

def test_analysis_and_history(tmp_path, monkeypatch):
    monkeypatch.setenv("REGIMPACT_DB_PATH", str(tmp_path / "reports.db"))
    response = client.post("/api/analyses", data={"profile": profile}, files={
        "earlier": ("earlier.txt", b"Rule 4 Registration\nEvery food operator shall maintain a register."),
        "updated": ("updated.txt", b"Rule 4 Registration\nEvery food operator shall submit a digital register by 30 June 2027."),
    })
    assert response.status_code == 200
    payload = response.json()
    assert payload["report"]["applicability"] == "Applies"
    assert client.get(f"/api/reports/{payload['id']}").status_code == 200
    assert client.get("/api/reports").json()[0]["id"] == payload["id"]

def test_demo_returns_expected_report(tmp_path, monkeypatch):
    monkeypatch.setenv("REGIMPACT_DB_PATH", str(tmp_path / "reports.db"))
    response = client.post("/api/demos/01_food_safety/analyses")
    assert response.status_code == 200
    assert response.json()["report"]["applicability"] == "Applies"

def test_action_status_persists(tmp_path, monkeypatch):
    monkeypatch.setenv("REGIMPACT_DB_PATH", str(tmp_path / "reports.db"))
    response = client.post("/api/demos/01_food_safety/analyses")
    action_id = response.json()["report"]["actions"][0]["task_id"]
    updated = client.patch(f"/api/actions/{action_id}", json={"status": "Completed"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "Completed"

def test_profile_can_be_saved_and_reused(tmp_path, monkeypatch):
    monkeypatch.setenv("REGIMPACT_DB_PATH", str(tmp_path / "profiles.db"))
    body = {"name": "Reusable SME", "industry": "food processing", "state": "Karnataka", "employee_count": None, "annual_turnover_lakh": None, "activities": "food operator", "registrations": "FSSAI"}
    assert client.post("/api/profiles", json=body).status_code == 200
    profiles = client.get("/api/profiles").json()
    assert profiles[0]["profile"]["employee_count"] is None

def test_rejects_unsupported_documents():
    response = client.post("/api/analyses", data={"profile": profile}, files={
        "earlier": ("earlier.docx", b"not supported"), "updated": ("updated.txt", b"Rule 1 Scope\nText")
    })
    assert response.status_code == 422
