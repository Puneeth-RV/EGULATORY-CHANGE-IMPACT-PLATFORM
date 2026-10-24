from __future__ import annotations
import json
from pathlib import Path
from .models import BusinessProfile, Change

RULES_PATH = Path(__file__).parents[1] / "rules" / "sample_rules.json"

def evaluate_rules(profile: BusinessProfile, changes: list[Change]) -> tuple[str, str, list[str], list[str]]:
    """Evaluate only explicit, checked-in demo rules; unknown regulations remain unverified."""
    payload = json.loads(RULES_PATH.read_text())
    changed = {change.clause_id.lower() for change in changes}
    for rule in payload["rules"]:
        if rule["clause"].lower() not in changed:
            continue
        used, missing, matches = [], [], []
        for condition in rule["conditions"]:
            attribute, expected = condition["attribute"], condition["value"]
            actual = getattr(profile, attribute, None)
            if actual is None or actual == "":
                missing.append(attribute); continue
            used.append(attribute)
            matches.append(str(expected).lower() in str(actual).lower() if condition["operator"] == "contains" else actual >= expected)
        if missing:
            return "Needs verification", f"Rule {rule['id']} needs the missing business attribute(s): {', '.join(missing)}.", used, missing
        if all(matches):
            return rule["outcome"], rule["explanation"], used, []
        return "Does not apply", f"Rule {rule['id']} was evaluated, but the supplied business attributes do not meet its stated condition(s).", used, []
    return "Needs verification", "No source-backed applicability rule is configured for the detected changed clauses. A qualified reviewer should confirm scope.", [], ["A source-backed rule for this regulation"]
