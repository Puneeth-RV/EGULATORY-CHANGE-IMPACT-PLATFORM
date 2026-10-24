from __future__ import annotations
import json, os, sqlite3
from pathlib import Path
from .models import BusinessProfile, ImpactReport

def connection(path: str | None = None) -> sqlite3.Connection:
    db = path or os.getenv("REGIMPACT_DB_PATH", "data/regimpact.db")
    Path(db).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY, created_at TEXT DEFAULT CURRENT_TIMESTAMP, business_name TEXT, report_json TEXT NOT NULL)")
    con.execute("CREATE TABLE IF NOT EXISTS actions (id INTEGER PRIMARY KEY, report_id INTEGER NOT NULL, action_json TEXT NOT NULL, status TEXT NOT NULL, FOREIGN KEY(report_id) REFERENCES reports(id))")
    con.execute("CREATE TABLE IF NOT EXISTS profiles (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, profile_json TEXT NOT NULL, updated_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    return con

def save_report(profile: BusinessProfile, report: ImpactReport, path: str | None = None) -> int:
    con = connection(path)
    cur = con.execute("INSERT INTO reports(business_name, report_json) VALUES (?, ?)", (profile.name, report.model_dump_json()))
    ident = int(cur.lastrowid)
    for action in report.actions:
        item = action.model_copy(update={"task_id": None})
        action_id = con.execute("INSERT INTO actions(report_id, action_json, status) VALUES (?, ?, ?)", (ident, item.model_dump_json(), action.status)).lastrowid
        action.task_id = int(action_id)
    con.execute("UPDATE reports SET report_json = ? WHERE id = ?", (report.model_dump_json(), ident))
    con.commit(); con.close()
    return ident

def update_action_status(action_id: int, status: str, path: str | None = None) -> dict | None:
    if status not in {"Not started", "In progress", "Completed", "Needs review"}:
        raise ValueError("Invalid action status")
    con = connection(path)
    row = con.execute("SELECT report_id, action_json FROM actions WHERE id = ?", (action_id,)).fetchone()
    if not row:
        con.close(); return None
    action = json.loads(row[1]); action["task_id"] = action_id; action["status"] = status
    con.execute("UPDATE actions SET status = ?, action_json = ? WHERE id = ?", (status, json.dumps(action), action_id))
    report_row = con.execute("SELECT report_json FROM reports WHERE id = ?", (row[0],)).fetchone()
    report = json.loads(report_row[0])
    report["actions"] = [action if item.get("task_id") == action_id else item for item in report["actions"]]
    con.execute("UPDATE reports SET report_json = ? WHERE id = ?", (json.dumps(report), row[0])); con.commit(); con.close()
    return action

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

def save_profile(profile: BusinessProfile, path: str | None = None) -> int:
    con = connection(path)
    con.execute("INSERT INTO profiles(name, profile_json) VALUES (?, ?) ON CONFLICT(name) DO UPDATE SET profile_json=excluded.profile_json, updated_at=CURRENT_TIMESTAMP", (profile.name, profile.model_dump_json()))
    row = con.execute("SELECT id FROM profiles WHERE name = ?", (profile.name,)).fetchone(); con.commit(); con.close()
    return int(row[0])

def list_profiles(path: str | None = None) -> list[dict]:
    con = connection(path)
    rows = con.execute("SELECT id, profile_json, updated_at FROM profiles ORDER BY updated_at DESC, id DESC").fetchall(); con.close()
    return [{"id": row[0], "profile": json.loads(row[1]), "updated_at": row[2]} for row in rows]
