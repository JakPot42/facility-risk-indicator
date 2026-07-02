"""Tests for risk_engine.py — deterministic scoring aggregation."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import FacilityInputs
from risk_engine import _tier_for_score, assess_facility


def _clean_facility() -> FacilityInputs:
    return FacilityInputs(
        facility_label="Clean Facility",
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


class TestAssessFacility:
    def test_clean_facility_scores_zero_low(self):
        result = assess_facility(_clean_facility())
        assert result.score == 0
        assert result.tier == "LOW"

    def test_facility_label_propagates(self):
        result = assess_facility(_clean_facility())
        assert result.facility_label == "Clean Facility"

    def test_returns_all_indicators_not_just_matched(self):
        result = assess_facility(_clean_facility())
        assert len(result.findings) == 8  # all indicators evaluated, matched or not

    def test_score_capped_at_100(self):
        f = _clean_facility()
        f.months_since_last_self_inspection = 30
        f.self_inspection_certified_current_year = False
        f.fso_tenure_months = None
        f.open_violation_count = 10
        f.violation_categories = {"physical_loss": 8, "data_spill": 2}
        f.open_vulnerability_count = 10
        f.months_since_last_dcsa_review = None
        result = assess_facility(f)
        assert result.score <= 100


class TestTierForScore:
    def test_boundaries(self):
        for score, expected in [(0, "LOW"), (25, "LOW"), (26, "MODERATE"), (50, "MODERATE"), (51, "HIGH"), (75, "HIGH"), (76, "CRITICAL"), (100, "CRITICAL")]:
            assert _tier_for_score(score) == expected
