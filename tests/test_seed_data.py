"""Tests for seed_data.py — fictional demo facility scenarios."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import seed_data
from risk_engine import assess_facility


class TestDemoFacilities:
    def test_all_four_scenarios_present(self):
        assert set(seed_data.DEMO_FACILITIES.keys()) == {"well_run", "moderate_risk", "high_risk", "naesoc_tier"}

    def test_facility_labels_marked_fictional(self):
        for inputs in seed_data.DEMO_FACILITIES.values():
            assert "fictional" in inputs.facility_label.lower()

    def test_well_run_scores_lower_than_high_risk(self):
        well_run = assess_facility(seed_data.DEMO_FACILITIES["well_run"])
        high_risk = assess_facility(seed_data.DEMO_FACILITIES["high_risk"])
        assert well_run.score < high_risk.score

    def test_high_risk_reaches_critical_tier(self):
        result = assess_facility(seed_data.DEMO_FACILITIES["high_risk"])
        assert result.tier == "CRITICAL"

    def test_naesoc_tier_facility_flagged_lower_complexity(self):
        result = assess_facility(seed_data.DEMO_FACILITIES["naesoc_tier"])
        context_finding = next(f for f in result.findings if f.indicator_id == "facility_oversight_context")
        assert context_finding.matched is True
