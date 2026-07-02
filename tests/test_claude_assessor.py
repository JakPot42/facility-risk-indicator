"""Tests for claude_assessor.py — DEMO_MODE deterministic path only (no
network calls)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from claude_assessor import generate_narrative
from models import FacilityInputs
from risk_engine import assess_facility


def _facility(**overrides) -> FacilityInputs:
    defaults = dict(
        facility_label="Test Facility",
        months_since_last_self_inspection=1,
        self_inspection_certified_current_year=True,
        fso_tenure_months=24,
        open_violation_count=0,
        violation_categories={},
        open_vulnerability_count=0,
        months_since_last_dcsa_review=3,
        possesses_classified_it_systems_onsite=True,
        stores_classified_material_onsite=True,
    )
    defaults.update(overrides)
    return FacilityInputs(**defaults)


class TestGenerateNarrative:
    def test_clean_facility_states_no_patterns_matched(self):
        result = assess_facility(_facility())
        text = generate_narrative(result)
        assert "No documented institutional risk patterns matched" in text

    def test_flagged_facility_lists_matched_findings(self):
        result = assess_facility(_facility(open_violation_count=8, violation_categories={"data_spill": 8}))
        text = generate_narrative(result)
        assert "Open Violation Count Outlier" in text

    def test_includes_remediation_steps(self):
        result = assess_facility(_facility(months_since_last_self_inspection=24))
        text = generate_narrative(result)
        assert "Remediation steps" in text
        assert "117.7" in text or "self-inspection" in text.lower()

    def test_always_ends_with_not_predictive_disclaimer(self):
        for facility in (_facility(), _facility(open_violation_count=10, violation_categories={"data_spill": 10})):
            result = assess_facility(facility)
            text = generate_narrative(result)
            assert "NOT predictive of any specific incident" in text

    def test_never_mentions_individual_person_language(self):
        result = assess_facility(_facility(fso_tenure_months=None, open_violation_count=8, violation_categories={"physical_loss": 8}))
        text = generate_narrative(result).lower()
        for forbidden in ("this employee", "this person", "the individual shows", "financial stress"):
            assert forbidden not in text
