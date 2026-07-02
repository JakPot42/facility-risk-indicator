"""config.py — cited indicator definitions, national baselines, and the
mandatory institutional/individual framing text. No logic lives here.

======================================================================
MANDATORY, NON-NEGOTIABLE FRAMING
======================================================================
This tool assesses INSTITUTIONAL / FACILITY-LEVEL security program
patterns only: violation counts, inspection cadence, certification
status, program-continuity clocks. It does NOT surveil, score, or
assess any individual person's behavior, psychology, finances, foreign
contacts, or any other personal circumstance. "This facility has 14
unresolved security violations pending" is institutional data this tool
uses. "This employee shows financial stress indicators" is individual
data this tool NEVER touches, collects, or infers.

DESIGN NOTE — FSO tenure (the one input closest to this line):
`fso_tenure_months` is stored as a bare integer (months since the
current FSO was appointed) computed by the facility manager before
input. This module and models.py deliberately have NO field for an
FSO's name, an appointment date, an employee ID, or anything else that
could be joined back to a specific identifiable person -- not merely
by convention, but because no such field exists in the data model at
all. The metric exists only to compare against the 6-month regulatory
training-completion clock in 32 CFR 117.12(d); it is a program-
continuity/compliance-timing fact about the ROLE, never an assessment
of whoever currently holds it.
======================================================================
"""
from __future__ import annotations

import os

DEMO_MODE = os.environ.get("DEMO_MODE", "True") == "True"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

SCOPE_DISCLAIMER = (
    "This tool assesses INSTITUTIONAL / FACILITY-LEVEL security program "
    "patterns only -- violation counts, inspection cadence, certification "
    "status. It does NOT surveil, score, or assess any individual "
    "person's behavior, psychology, finances, or personal circumstances. "
    "It is NOT predictive of specific incidents."
)

# ---------------------------------------------------------------------------
# National baselines — GAO-26-107861, "Industrial Security: Improved Risk
# Management and Stakeholder Engagement Needed to Help DOD Address Mission
# Gaps" (U.S. Government Accountability Office, April 24, 2026).
# ---------------------------------------------------------------------------
GAO_REPORT_CITATION = (
    "GAO-26-107861, \"Industrial Security: Improved Risk Management and "
    "Stakeholder Engagement Needed to Help DOD Address Mission Gaps\" "
    "(U.S. Government Accountability Office, April 24, 2026)."
)
GAO_FY2025_SECURITY_REVIEWS = 4600          # DCSA security reviews conducted, FY2025
GAO_FY2025_VIOLATIONS = 815                  # security violations documented, FY2025
GAO_SEP2025_OPEN_VULNERABILITIES = 1032       # open security vulnerabilities, as of Sept 2025
GAO_NATIONAL_AVG_VIOLATIONS_PER_REVIEW = round(GAO_FY2025_VIOLATIONS / GAO_FY2025_SECURITY_REVIEWS, 3)
GAO_INSPECTION_COMPLETION_RATE = 0.40         # DCSA completed "less than 40%" of required inspections, FY2025
GAO_2023_OVERSIGHT_COVERAGE_LOW = 0.25        # DCSA funded to oversee only 25-30% of cleared industrial base (2023 finding)
GAO_2023_OVERSIGHT_COVERAGE_HIGH = 0.30

# Violation category mix, FY2025 (GAO-26-107861) — used only to compare a
# facility's own reported category mix against the documented national
# distribution, never to infer anything about a person.
GAO_VIOLATION_CATEGORY_MIX = {
    "data_spill": 0.60,
    "improper_storage": 0.115,
    "access_breach_or_unauthorized_disclosure": 0.065,
    "physical_loss": 0.063,
    "improper_physical_transfer": 0.056,
}

# ---------------------------------------------------------------------------
# NISPOM (32 CFR Part 117) citations
# ---------------------------------------------------------------------------
NISPOM_SELF_INSPECTION_CITATION = (
    "32 CFR 117.7(a) -- contractors must review their security program on "
    "a continuing basis and conduct a formal self-inspection at least "
    "annually and at intervals consistent with risk management principles; "
    "DCSA interprets \"annually\" as once every calendar year."
)
NISPOM_SELF_INSPECTION_CERTIFICATION_CITATION = (
    "32 CFR 117.7 -- the Senior Management Official (SMO) must annually "
    "certify to the CSA, in writing, that a self-inspection has been "
    "conducted, that other Key Management Personnel (KMP) have been "
    "briefed on the results, that appropriate corrective actions have "
    "been taken, and that management fully supports the security program."
)
NISPOM_FSO_TRAINING_CITATION = (
    "32 CFR 117.12(d) -- contractor FSOs must complete required security "
    "training within 6 months of appointment to the FSO position."
)

# ---------------------------------------------------------------------------
# Thresholds — where a specific number isn't published by GAO/NISPOM (e.g.
# an exact per-facility violation-count percentile), the threshold below is
# a documented, disclosed simplification: a round multiple of the national
# per-review average, not a statistically derived cutoff. See README
# "How thresholds were chosen."
# ---------------------------------------------------------------------------
SELF_INSPECTION_OVERDUE_MONTHS = 12          # NISPOM minimum: "at least annually"
SELF_INSPECTION_SEVERELY_OVERDUE_MONTHS = 24  # 2x the NISPOM minimum

FSO_TRAINING_WINDOW_MONTHS = 6                # 32 CFR 117.12(d)

# A facility with >= this many open violations is a documented outlier
# against the FY2025 national per-review average (~0.18); this threshold
# is roughly 15x that average, chosen as a round, clearly-outlying number
# rather than a precise percentile GAO did not publish.
VIOLATION_COUNT_MODERATE = 3
VIOLATION_COUNT_HIGH = 6

VULNERABILITY_COUNT_MODERATE = 3
VULNERABILITY_COUNT_HIGH = 6

# DCSA review overdue: GAO found DCSA completing under 40% of required
# inspections nationally and, per 2023 findings, resourced for only
# 25-30% coverage -- a facility significantly overdue for external review
# is consistent with (not necessarily caused by) that documented national
# gap. 24 months is used as "significantly overdue" -- double a typical
# annual-cycle expectation -- not a specific DCSA-published interval.
DCSA_REVIEW_OVERDUE_MONTHS = 24

# A non-data-spill violation category representing more than this share of
# a facility's OWN violations is notable because every non-data-spill
# category sits under 12% nationally (GAO_VIOLATION_CATEGORY_MIX above).
VIOLATION_CATEGORY_CONCENTRATION_THRESHOLD = 0.25
VIOLATION_CATEGORY_CONCENTRATION_MIN_COUNT = 2  # don't flag concentration off a single violation

# ---------------------------------------------------------------------------
# Risk tiers
# ---------------------------------------------------------------------------
RISK_TIERS = [
    (25, "LOW"),
    (50, "MODERATE"),
    (75, "HIGH"),
]
RISK_TIER_DEFAULT = "CRITICAL"
