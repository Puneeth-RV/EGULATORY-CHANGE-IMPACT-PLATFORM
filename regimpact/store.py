from __future__ import annotations
import json, os, sqlite3
from pathlib import Path
from .models import BusinessProfile, ImpactReport

def connection(path: str | None = None) -> sqlite3.Connection:
    db = path or os.getenv("REGIMPACT_DB_PATH", "data/regimpact.db")
    Path(db).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY, created_at TEXT DEFAULT CURRENT_TIMESTAMP, business_name TEXT, report_json TEXT NOT NULL)")
    return con

def save_report(profile: BusinessProfile, report: ImpactReport, path: str | None = None) -> int:
    con = connection(path)
    cur = con.execute("INSERT INTO reports(business_name, report_json) VALUES (?, ?)", (profile.name, report.model_dump_json()))
    con.commit(); ident = cur.lastrowid; con.close()
    return int(ident)

def recent_reports(path: str | None = None) -> list[dict]:
    con = connection(path)
    rows = con.execute("SELECT id, created_at, business_name, report_json FROM reports ORDER BY id DESC LIMIT 10").fetchall(); con.close()
    return [{"id": r[0], "created_at": r[1], "business_name": r[2], "report": json.loads(r[3])} for r in rows]

def get_report(report_id: int, path: str | None = None) -> dict | None:
    con = connection(path)
    row = con.execute("SELECT id, created_at, business_name, report_json FROM reports WHERE id = ?", (report_id,)).fetchone(); con.close()
    if not row:
        return None
    return {"id": row[0], "created_at": row[1], "business_name": row[2], "report": json.loads(row[3])}
