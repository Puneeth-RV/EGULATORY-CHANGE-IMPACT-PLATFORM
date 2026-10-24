"""Optional Gemini interpretation, isolated from the evidence/diff pipeline."""
from __future__ import annotations
import os
from .models import ActionItem, BusinessProfile, Change

def enrich_actions(profile: BusinessProfile, changes: list[Change]) -> list[ActionItem] | None:
    """Return plain-language actions validated by Pydantic, or None if not configured.

    The deterministic diff remains authoritative; Gemini only translates supplied
    evidence into operational language and is never called without an explicit key.
    """
    key = os.getenv("GEMINI_API_KEY")
    if not key or not changes:
        return None
    from google import genai
    client = genai.Client(api_key=key)
    evidence = "\n\n".join(f"{c.clause_id} (page {c.page}): {c.new_text or c.old_text}" for c in changes)
    prompt = f"""You are a careful Indian SME compliance assistant. Based ONLY on this evidence,
write practical action items for this business profile: {profile.model_dump_json()}.
Do not invent deadlines; use 'Not specified in the supplied update' when absent.
Return a JSON array matching this schema: {ActionItem.model_json_schema()}.
Evidence:\n{evidence}"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )
    import json
    payload = json.loads(response.text)
    return [ActionItem.model_validate(item) for item in payload]
