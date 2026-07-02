"""models.py — shared dataclasses. No logic.

FacilityInputs is deliberately the ONLY place facility data enters this
tool, and it is deliberately incapable of representing an identifiable
person. There is no name field, no employee ID field, no appointment-
date field, no free-text field of any kind. `fso_tenure_months` is a
bare integer the facility manager computes themselves before typing it
in -- this module has no way to derive it from, or join it back to, a
specific person. This is a structural guarantee, not a naming
convention: if a future change needs to add a field here, the absence of
any free-text or identifier field should be the thing that makes adding
individual-level data feel like it doesn't fit, not a comment telling
you not to.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FacilityInputs:
    """Every field here is a facility-level operational fact. None of
    them, individually or combined, identify a person."""

    facility_label: str  # a facility name/identifier the MANAGER chooses for their own reference (e.g. "Building 4"), never a person's name

    months_since_last_self_inspection: int
    self_inspection_certified_current_year: bool

    fso_tenure_months: int | None  # None means the FSO position is currently vacant -- see indicators.py

    open_violation_count: int
    violation_categories: dict[str, int] = field(default_factory=dict)  # category -> count, from config.GAO_VIOLATION_CATEGORY_MIX keys

    open_vulnerability_count: int = 0
    months_since_last_dcsa_review: int | None = None  # None means never reviewed or unknown

    possesses_classified_it_systems_onsite: bool = False
    stores_classified_material_onsite: bool = False


@dataclass
class Finding:
    indicator_id: str
    label: str
    matched: bool
    severity: str          # "INFORMATIONAL" | "MODERATE" | "HIGH"
    points: int
    explanation: str
    citation: str
    remediation: str


@dataclass
class AssessmentResult:
    facility_label: str
    findings: list[Finding]
    score: int
    tier: str
