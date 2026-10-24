from __future__ import annotations
from datetime import date
from typing import Literal
from pydantic import BaseModel, Field

class BusinessProfile(BaseModel):
    name: str
    industry: str
    state: str = "India"
    employee_count: int = 0
    annual_turnover_lakh: float = 0
    activities: str = ""
    registrations: str = ""

class Clause(BaseModel):
    identifier: str
    text: str
    page: int = 1

class Change(BaseModel):
    change_type: Literal["added", "removed", "modified"]
    clause_id: str
    old_text: str = ""
    new_text: str = ""
    page: int = 1
    summary: str
    evidence: str

class ActionItem(BaseModel):
    action: str
    deadline: str = "Not specified in the supplied update"
    owner: str = "Compliance coordinator"
    priority: Literal["High", "Medium", "Low"] = "Medium"
    evidence: str

class ImpactReport(BaseModel):
    applicability: Literal["Likely applies", "Possibly applies", "Unlikely to apply", "Needs review"]
    rationale: str
    changes: list[Change] = Field(default_factory=list)
    actions: list[ActionItem] = Field(default_factory=list)
    caveat: str = "This is an operational aid, not legal advice. Verify material decisions against the official notification."
