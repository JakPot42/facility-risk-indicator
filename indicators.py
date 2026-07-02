"""indicators.py — deterministic institutional risk indicators.

Every function here takes FacilityInputs (facility-level operational
facts only -- see models.py) and returns a Finding. Nothing here reads,
stores, or infers anything about a specific person. Every indicator
cites a real, checkable source (config.py) -- no invented thresholds.
"""
from __future__ import annotations

from config import (
    DCSA_REVIEW_OVERDUE_MONTHS,
    FSO_TRAINING_WINDOW_MONTHS,
    GAO_REPORT_CITATION,
    GAO_VIOLATION_CATEGORY_MIX,
    NISPOM_FSO_TRAINING_CITATION,
    NISPOM_SELF_INSPECTION_CERTIFICATION_CITATION,
    NISPOM_SELF_INSPECTION_CITATION,
    SELF_INSPECTION_OVERDUE_MONTHS,
    SELF_INSPECTION_SEVERELY_OVERDUE_MONTHS,
    VIOLATION_CATEGORY_CONCENTRATION_MIN_COUNT,
    VIOLATION_CATEGORY_CONCENTRATION_THRESHOLD,
    VIOLATION_COUNT_HIGH,
    VIOLATION_COUNT_MODERATE,
    VULNERABILITY_COUNT_HIGH,
    VULNERABILITY_COUNT_MODERATE,
)
from models import FacilityInputs, Finding


def self_inspection_overdue(f: FacilityInputs) -> Finding:
    months = f.months_since_last_self_inspection
    if months >= SELF_INSPECTION_SEVERELY_OVERDUE_MONTHS:
        return Finding(
            indicator_id="self_inspection_overdue",
            label="Self-Inspection Severely Overdue",
            matched=True, severity="HIGH", points=25,
            explanation=(
                f"{months} months since the last documented self-inspection -- "
                f"more than double the NISPOM minimum of 12 months."
            ),
            citation=NISPOM_SELF_INSPECTION_CITATION,
            remediation=(
                "Conduct and document a formal self-inspection immediately per "
                "32 CFR 117.7(a); do not wait for the next DCSA-scheduled review."
            ),
        )
    if months >= SELF_INSPECTION_OVERDUE_MONTHS:
        return Finding(
            indicator_id="self_inspection_overdue",
            label="Self-Inspection Overdue",
            matched=True, severity="MODERATE", points=15,
            explanation=f"{months} months since the last documented self-inspection, exceeding the NISPOM annual minimum.",
            citation=NISPOM_SELF_INSPECTION_CITATION,
            remediation="Schedule and document a formal self-inspection within 30 days per 32 CFR 117.7(a).",
        )
    return Finding(
        indicator_id="self_inspection_overdue", label="Self-Inspection Overdue",
        matched=False, severity="INFORMATIONAL", points=0,
        explanation=f"{months} months since the last self-inspection -- within the NISPOM annual requirement.",
        citation=NISPOM_SELF_INSPECTION_CITATION, remediation="",
    )


def self_inspection_certification_missing(f: FacilityInputs) -> Finding:
    if not f.self_inspection_certified_current_year:
        return Finding(
            indicator_id="self_inspection_certification_missing",
            label="Self-Inspection Certification Missing",
            matched=True, severity="MODERATE", points=15,
            explanation="No current-year written SMO certification of self-inspection completion on file.",
            citation=NISPOM_SELF_INSPECTION_CERTIFICATION_CITATION,
            remediation=(
                "Have the Senior Management Official complete and file the "
                "written annual certification required by 32 CFR 117.7 -- self-"
                "inspection conducted, KMP briefed, corrective actions taken."
            ),
        )
    return Finding(
        indicator_id="self_inspection_certification_missing", label="Self-Inspection Certification Missing",
        matched=False, severity="INFORMATIONAL", points=0,
        explanation="Current-year SMO self-inspection certification is on file.",
        citation=NISPOM_SELF_INSPECTION_CERTIFICATION_CITATION, remediation="",
    )


def fso_position_status(f: FacilityInputs) -> Finding:
    """Reads ONLY fso_tenure_months (a bare integer). See models.py's
    module docstring and config.py's design note: this indicator never
    touches, and cannot touch, anything identifying who holds the role."""
    if f.fso_tenure_months is None:
        return Finding(
            indicator_id="fso_position_status", label="FSO Position Vacant",
            matched=True, severity="HIGH", points=25,
            explanation="No Facility Security Officer currently designated -- NISPOM requires an FSO be appointed at all times.",
            citation=NISPOM_FSO_TRAINING_CITATION,
            remediation="Designate a Facility Security Officer immediately; the 6-month training-completion clock (32 CFR 117.12(d)) starts at appointment.",
        )
    if f.fso_tenure_months < FSO_TRAINING_WINDOW_MONTHS:
        return Finding(
            indicator_id="fso_position_status", label="FSO Position Within Training-Completion Window",
            matched=True, severity="INFORMATIONAL", points=5,
            explanation=(
                f"The FSO position was appointed {f.fso_tenure_months} month(s) ago, inside the "
                f"{FSO_TRAINING_WINDOW_MONTHS}-month regulatory training-completion window. This is a "
                f"program-continuity/compliance-timing fact about the ROLE, not an assessment of "
                f"whoever currently holds it."
            ),
            citation=NISPOM_FSO_TRAINING_CITATION,
            remediation="Confirm required FSO training is scheduled to complete before the 6-month deadline in 32 CFR 117.12(d).",
        )
    return Finding(
        indicator_id="fso_position_status", label="FSO Position Within Training-Completion Window",
        matched=False, severity="INFORMATIONAL", points=0,
        explanation=f"The FSO position has been filled for {f.fso_tenure_months} months, past the 6-month training window.",
        citation=NISPOM_FSO_TRAINING_CITATION, remediation="",
    )


def violation_count_outlier(f: FacilityInputs) -> Finding:
    n = f.open_violation_count
    if n >= VIOLATION_COUNT_HIGH:
        severity, points = "HIGH", 25
    elif n >= VIOLATION_COUNT_MODERATE:
        severity, points = "MODERATE", 15
    else:
        severity, points = "INFORMATIONAL", 0

    return Finding(
        indicator_id="violation_count_outlier", label="Open Violation Count Outlier",
        matched=points > 0, severity=severity, points=points,
        explanation=(
            f"{n} open violation(s) on file. {GAO_REPORT_CITATION.split(',')[0]} documented "
            f"815 violations across 4,600+ FY2025 DCSA security reviews nationally "
            f"(~0.18 per review) -- {n} is well above that per-facility average."
            if points > 0 else
            f"{n} open violation(s) on file -- not a documented outlier against the FY2025 national average."
        ),
        citation=GAO_REPORT_CITATION,
        remediation=(
            "Prioritize resolution of open violations and document corrective "
            "action timelines; review whether violations cluster in a specific "
            "program area (see Violation Category Concentration finding)."
            if points > 0 else ""
        ),
    )


def vulnerability_count_outlier(f: FacilityInputs) -> Finding:
    n = f.open_vulnerability_count
    if n >= VULNERABILITY_COUNT_HIGH:
        severity, points = "HIGH", 20
    elif n >= VULNERABILITY_COUNT_MODERATE:
        severity, points = "MODERATE", 10
    else:
        severity, points = "INFORMATIONAL", 0

    return Finding(
        indicator_id="vulnerability_count_outlier", label="Open Vulnerability Count Outlier",
        matched=points > 0, severity=severity, points=points,
        explanation=(
            f"{n} open vulnerability(ies) on file. {GAO_REPORT_CITATION.split(',')[0]} documented "
            f"1,032 open vulnerabilities nationally as of September 2025."
            if points > 0 else
            f"{n} open vulnerability(ies) on file."
        ),
        citation=GAO_REPORT_CITATION,
        remediation="Prioritize remediation of open vulnerabilities and document closure timelines." if points > 0 else "",
    )


def dcsa_review_overdue(f: FacilityInputs) -> Finding:
    months = f.months_since_last_dcsa_review
    if months is None or months >= DCSA_REVIEW_OVERDUE_MONTHS:
        display = "never reviewed / unknown" if months is None else f"{months} months"
        return Finding(
            indicator_id="dcsa_review_overdue", label="DCSA Review Significantly Overdue",
            matched=True, severity="MODERATE", points=15,
            explanation=(
                f"Time since last DCSA security review: {display}. {GAO_REPORT_CITATION.split(',')[0]} found "
                f"DCSA completed under 40% of required inspections in FY2025 and was resourced to oversee only "
                f"25-30% of the cleared industrial base as of 2023 -- a facility significantly overdue for "
                f"external review is consistent with that documented national coverage gap, meaning self-"
                f"inspection rigor carries more real weight in the interim."
            ),
            citation=GAO_REPORT_CITATION,
            remediation="Request a DCSA security review; in the interim, increase self-inspection frequency beyond the annual minimum.",
        )
    return Finding(
        indicator_id="dcsa_review_overdue", label="DCSA Review Significantly Overdue",
        matched=False, severity="INFORMATIONAL", points=0,
        explanation=f"Time since last DCSA security review: {months} months.",
        citation=GAO_REPORT_CITATION, remediation="",
    )


def violation_category_concentration(f: FacilityInputs) -> Finding:
    total = sum(f.violation_categories.values())
    if total < VIOLATION_CATEGORY_CONCENTRATION_MIN_COUNT:
        return Finding(
            indicator_id="violation_category_concentration", label="Violation Category Concentration",
            matched=False, severity="INFORMATIONAL", points=0,
            explanation="Too few reported violations to assess category concentration.",
            citation=GAO_REPORT_CITATION, remediation="",
        )

    concentrated = []
    for category, count in f.violation_categories.items():
        if category == "data_spill":
            continue  # dominant nationally (60%) -- concentration there isn't an outlier
        share = count / total
        national_share = GAO_VIOLATION_CATEGORY_MIX.get(category, 0.0)
        if share >= VIOLATION_CATEGORY_CONCENTRATION_THRESHOLD and share > national_share:
            concentrated.append((category, share, national_share))

    if concentrated:
        details = "; ".join(f"{cat} at {share:.0%} of this facility's violations vs {nat:.1%} nationally" for cat, share, nat in concentrated)
        return Finding(
            indicator_id="violation_category_concentration", label="Violation Category Concentration",
            matched=True, severity="MODERATE", points=10,
            explanation=f"This facility's violation mix is concentrated in a category uncommon nationally: {details}.",
            citation=GAO_REPORT_CITATION,
            remediation="Review whether a specific program area (e.g. physical security, storage, transfer procedures) needs targeted process correction.",
        )
    return Finding(
        indicator_id="violation_category_concentration", label="Violation Category Concentration",
        matched=False, severity="INFORMATIONAL", points=0,
        explanation="This facility's violation category mix does not show a notable concentration vs. the national mix.",
        citation=GAO_REPORT_CITATION, remediation="",
    )


def facility_oversight_context(f: FacilityInputs) -> Finding:
    """Contextual only -- never contributes points. Flags whether this
    facility falls into the lower-complexity tier GAO-26-107861 describes
    DCSA's NAESOC (National Access Elsewhere Security Oversight Center,
    est. 2019) as serving: facilities without classified IT systems or
    classified material on-site."""
    lower_complexity = not f.possesses_classified_it_systems_onsite and not f.stores_classified_material_onsite
    return Finding(
        indicator_id="facility_oversight_context", label="Facility Oversight Complexity Context",
        matched=lower_complexity, severity="INFORMATIONAL", points=0,
        explanation=(
            "This facility does not possess classified IT systems or store classified "
            "material on-site -- the lower-complexity tier DCSA's National Access Elsewhere "
            "Security Oversight Center (NAESOC, est. 2019) was created to advise and assist."
            if lower_complexity else
            "This facility possesses classified IT systems and/or stores classified material on-site -- the higher-complexity oversight tier."
        ),
        citation=GAO_REPORT_CITATION,
        remediation="",
    )


ALL_INDICATORS = [
    self_inspection_overdue,
    self_inspection_certification_missing,
    fso_position_status,
    violation_count_outlier,
    vulnerability_count_outlier,
    dcsa_review_overdue,
    violation_category_concentration,
    facility_oversight_context,
]


def evaluate_all(f: FacilityInputs) -> list[Finding]:
    return [indicator(f) for indicator in ALL_INDICATORS]
