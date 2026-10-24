from __future__ import annotations
import difflib
import re
from .models import ActionItem, BusinessProfile, Change, Clause, ImpactReport

DEADLINE = re.compile(r"(?:by|before|within)\s+(?:the\s+)?(?:\d+\s+(?:days|months)|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4})", re.I)
ACTION_WORDS = re.compile(r"\b(must|shall|required|file|submit|register|maintain|display|pay|issue|obtain|renew|update|comply)\b", re.I)

def compact(text: str, length: int = 240) -> str:
    text = " ".join(text.split())
    return text if len(text) <= length else text[: length - 1] + "…"

def detect_changes(old: list[Clause], new: list[Clause]) -> list[Change]:
    old_map, new_map = {c.identifier.lower(): c for c in old}, {c.identifier.lower(): c for c in new}
    changes: list[Change] = []
    for key, clause in new_map.items():
        before = old_map.get(key)
        if before is None:
            changes.append(Change(change_type="added", clause_id=clause.identifier, new_text=clause.text, page=clause.page, summary=f"New requirement/text added in {clause.identifier}.", evidence=compact(clause.text)))
        elif before.text != clause.text:
            changes.append(Change(change_type="modified", clause_id=clause.identifier, old_text=before.text, new_text=clause.text, page=clause.page, summary=f"Wording changed in {clause.identifier}.", evidence=f"Before: {compact(before.text, 110)} | After: {compact(clause.text, 110)}"))
    for key, clause in old_map.items():
        if key not in new_map:
            changes.append(Change(change_type="removed", clause_id=clause.identifier, old_text=clause.text, page=clause.page, summary=f"Text removed from {clause.identifier}.", evidence=compact(clause.text)))
    # Heading-free documents: produce a useful whole-document diff.
    if not changes and old and new and old[0].text != new[0].text:
        changes.append(Change(change_type="modified", clause_id="Document text", old_text=old[0].text, new_text=new[0].text, page=new[0].page, summary="Document wording changed.", evidence=" ".join(difflib.unified_diff([compact(old[0].text)], [compact(new[0].text)], lineterm=""))))
    return changes

def assess(profile: BusinessProfile, changes: list[Change]) -> tuple[str, str]:
    corpus = " ".join((c.new_text or c.old_text) for c in changes).lower()
    profile_words = set(re.findall(r"[a-z]{4,}", " ".join([profile.industry, profile.activities, profile.registrations, profile.state]).lower()))
    matches = [w for w in profile_words if w in corpus]
    turnover_match = bool(re.search(r"turnover|crore|lakh", corpus))
    employee_match = bool(re.search(r"employee|worker|staff", corpus))
    if matches:
        return "Likely applies", "The update explicitly overlaps with your profile: " + ", ".join(matches[:5]) + "."
    if turnover_match or employee_match:
        return "Possibly applies", "The update includes size-based conditions. Confirm its threshold against your business profile."
    if not changes:
        return "Needs review", "No material textual difference was detected from the supplied documents."
    return "Needs review", "No direct profile match was found in the changed text; review scope and definitions in the official notification."

def action_items(changes: list[Change], applicable: str) -> list[ActionItem]:
    if applicable == "Unlikely to apply": return []
    output: list[ActionItem] = []
    for change in changes:
        text = change.new_text or change.old_text
        if ACTION_WORDS.search(text):
            deadline = DEADLINE.search(text)
            output.append(ActionItem(action=f"Review and implement the obligation in {change.clause_id}: {compact(text, 180)}", deadline=deadline.group(0) if deadline else "Not specified in the supplied update", priority="High" if deadline else "Medium", evidence=f"{change.clause_id}, page {change.page}: {compact(text, 220)}"))
    if not output and changes:
        c = changes[0]
        output.append(ActionItem(action=f"Review the operational impact of the change in {c.clause_id} and obtain advice if it affects your business.", evidence=c.evidence, priority="Medium"))
    return output

def analyze(old: list[Clause], new: list[Clause], profile: BusinessProfile) -> ImpactReport:
    changes = detect_changes(old, new)
    applicability, rationale = assess(profile, changes)
    return ImpactReport(applicability=applicability, rationale=rationale, changes=changes, actions=action_items(changes, applicability))
