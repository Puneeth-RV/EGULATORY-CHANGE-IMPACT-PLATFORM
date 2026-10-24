from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

class BusinessProfile(BaseModel):
    name: str
    industry: str
    state: str = "India"
    employee_count: int | None = None
    annual_turnover_lakh: float | None = None
    activities: str | None = None
    registrations: str | None = None

class Clause(BaseModel):
    identifier: str
    text: str
    page: int = 1

class Change(BaseModel):
    change_id: str = ""
    change_type: Literal["added", "removed", "modified"]
    clause_id: str
    old_text: str = ""
    new_text: str = ""
    page: int = 1
    old_page: int | None = None
    new_page: int | None = None
    comparison_status: Literal["matched", "needs_review"] = "matched"
    confidence: float = 1.0
    summary: str
    evidence: str

class ActionItem(BaseModel):
    task_id: int | None = None
    action: str
    reason: str = ""
    supporting_clause: str = ""
    deadline: str = "Deadline not established from the available source."
    owner: str = "Compliance coordinator"
    priority: Literal["High", "Medium", "Low"] = "Medium"
    status: Literal["Not started", "In progress", "Completed", "Needs review"] = "Not started"
    evidence: str

class ImpactReport(BaseModel):
    applicability: Literal["Applies", "Does not apply", "Needs verification"]
    rationale: str
    attributes_used: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    changes: list[Change] = Field(default_factory=list)
    actions: list[ActionItem] = Field(default_factory=list)
    caveat: str = "This is an operational aid, not legal advice. Verify material decisions against the official notification."
