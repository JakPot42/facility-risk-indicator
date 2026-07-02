"""risk_engine.py — deterministic aggregation of Findings into a score
and tier. Claude never scores; every point comes from indicators.py's
cited rules. "Claude extracts, rules decide."
"""
from __future__ import annotations

from config import RISK_TIER_DEFAULT, RISK_TIERS
from indicators import evaluate_all
from models import AssessmentResult, FacilityInputs


def _tier_for_score(score: int) -> str:
    for ceiling, tier in RISK_TIERS:
        if score <= ceiling:
            return tier
    return RISK_TIER_DEFAULT


def assess_facility(inputs: FacilityInputs) -> AssessmentResult:
    findings = evaluate_all(inputs)
    score = min(100, sum(f.points for f in findings))
    return AssessmentResult(
        facility_label=inputs.facility_label,
        findings=findings,
        score=score,
        tier=_tier_for_score(score),
    )
