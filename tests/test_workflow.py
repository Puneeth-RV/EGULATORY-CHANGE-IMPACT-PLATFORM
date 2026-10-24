from regimpact.analysis import analyze, detect_changes
from regimpact.documents import parse_clauses
from regimpact.models import BusinessProfile
from regimpact.store import recent_reports, save_report

OLD = [(1, "Rule 4 Registration\nEvery food operator shall maintain a register.")]
NEW = [(1, "Rule 4 Registration\nEvery food operator shall maintain a digital register and submit it by 30 June 2027.")]

def test_parser_preserves_identifier():
    assert parse_clauses(NEW)[0].identifier == "Rule 4"

def test_end_to_end_analysis_and_storage(tmp_path):
    profile = BusinessProfile(name="A", industry="food", activities="food operator")
    report = analyze(parse_clauses(OLD), parse_clauses(NEW), profile)
    assert report.applicability == "Likely applies"
    assert len(report.changes) == 1
    assert report.actions[0].deadline.lower() == "by 30 june 2027"
    db = str(tmp_path / "test.db")
    save_report(profile, report, db)
    assert recent_reports(db)[0]["business_name"] == "A"

def test_added_clause_is_reported():
    changes = detect_changes(parse_clauses([(1, "Rule 1 Scope\nFood operators.")]), parse_clauses([(1, "Rule 1 Scope\nFood operators.\nRule 2 Filing\nOperators shall file monthly returns.")]))
    assert any(c.change_type == "added" for c in changes)
