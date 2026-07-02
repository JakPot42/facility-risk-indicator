"""Tests for indicators.py — every indicator, boundary conditions, and
citation presence."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from indicators import (
    ALL_INDICATORS,
    dcsa_review_overdue,
    facility_oversight_context,
    fso_position_status,
    self_inspection_certification_missing,
    self_inspection_overdue,
    violation_category_concentration,
    violation_count_outlier,
    vulnerability_count_outlier,
)
from models import FacilityInputs


def _base(**overrides) -> FacilityInputs:
    defaults = dict(
        facility_label="Test Facility",
        months_since_last_self_inspection=3,
        self_inspection_certified_current_year=True,
        fso_tenure_months=24,
        open_violation_count=0,
        violation_categories={},
        open_vulnerability_count=0,
        months_since_last_dcsa_review=6,
        possesses_classified_it_systems_onsite=True,
        stores_classified_material_onsite=True,
    )
    defaults.update(overrides)
    return FacilityInputs(**defaults)


class TestSelfInspectionOverdue:
    def test_within_annual_requirement_not_matched(self):
        f = self_inspection_overdue(_base(months_since_last_self_inspection=11))
        assert f.matched is False

    def test_exactly_12_months_matches_moderate(self):
        f = self_inspection_overdue(_base(months_since_last_self_inspection=12))
        assert f.matched is True and f.severity == "MODERATE"

    def test_24_months_matches_high(self):
        f = self_inspection_overdue(_base(months_since_last_self_inspection=24))
        assert f.matched is True and f.severity == "HIGH"

    def test_citation_present(self):
        f = self_inspection_overdue(_base())
        assert "117.7" in f.citation


class TestSelfInspectionCertificationMissing:
    def test_certified_not_matched(self):
        f = self_inspection_certification_missing(_base(self_inspection_certified_current_year=True))
        assert f.matched is False

    def test_not_certified_matches(self):
        f = self_inspection_certification_missing(_base(self_inspection_certified_current_year=False))
        assert f.matched is True
        assert f.severity == "MODERATE"


class TestFsoPositionStatus:
    def test_vacant_position_matches_high(self):
        f = fso_position_status(_base(fso_tenure_months=None))
        assert f.matched is True and f.severity == "HIGH"

    def test_within_training_window_matches_informational(self):
        f = fso_position_status(_base(fso_tenure_months=3))
        assert f.matched is True and f.severity == "INFORMATIONAL"
        assert f.points == 5

    def test_past_training_window_not_matched(self):
        f = fso_position_status(_base(fso_tenure_months=6))
        assert f.matched is False

    def test_citation_is_117_12d(self):
        f = fso_position_status(_base(fso_tenure_months=None))
        assert "117.12(d)" in f.citation

    def test_explanation_never_names_a_person(self):
        # Regression guard: the explanation string must describe the
        # ROLE/position, never claim anything about who holds it.
        f = fso_position_status(_base(fso_tenure_months=3))
        assert "the role" in f.explanation.lower() or "the fso position" in f.explanation.lower() or "whoever" in f.explanation.lower()


class TestViolationCountOutlier:
    def test_below_moderate_threshold_not_matched(self):
        f = violation_count_outlier(_base(open_violation_count=2))
        assert f.matched is False

    def test_at_moderate_threshold_matches(self):
        f = violation_count_outlier(_base(open_violation_count=3))
        assert f.matched is True and f.severity == "MODERATE"

    def test_at_high_threshold_matches(self):
        f = violation_count_outlier(_base(open_violation_count=6))
        assert f.matched is True and f.severity == "HIGH"

    def test_citation_is_gao_report(self):
        f = violation_count_outlier(_base(open_violation_count=6))
        assert "GAO-26-107861" in f.citation


class TestVulnerabilityCountOutlier:
    def test_below_threshold_not_matched(self):
        f = vulnerability_count_outlier(_base(open_vulnerability_count=2))
        assert f.matched is False

    def test_at_high_threshold_matches(self):
        f = vulnerability_count_outlier(_base(open_vulnerability_count=6))
        assert f.matched is True and f.severity == "HIGH"


class TestDcsaReviewOverdue:
    def test_recent_review_not_matched(self):
        f = dcsa_review_overdue(_base(months_since_last_dcsa_review=6))
        assert f.matched is False

    def test_overdue_matches(self):
        f = dcsa_review_overdue(_base(months_since_last_dcsa_review=24))
        assert f.matched is True

    def test_never_reviewed_matches(self):
        f = dcsa_review_overdue(_base(months_since_last_dcsa_review=None))
        assert f.matched is True
        assert "never reviewed" in f.explanation.lower()


class TestViolationCategoryConcentration:
    def test_too_few_violations_not_matched(self):
        f = violation_category_concentration(_base(violation_categories={"physical_loss": 1}))
        assert f.matched is False

    def test_data_spill_concentration_not_flagged(self):
        # data_spill is nationally dominant (60%) -- concentration there is expected, not an outlier.
        f = violation_category_concentration(_base(violation_categories={"data_spill": 5}))
        assert f.matched is False

    def test_physical_loss_concentration_flagged(self):
        f = violation_category_concentration(_base(violation_categories={"data_spill": 1, "physical_loss": 4}))
        assert f.matched is True
        assert "physical_loss" in f.explanation

    def test_evenly_spread_categories_not_flagged(self):
        f = violation_category_concentration(_base(violation_categories={
            "data_spill": 2, "improper_storage": 1, "physical_loss": 1, "access_breach_or_unauthorized_disclosure": 1,
        }))
        assert f.matched is False


class TestFacilityOversightContext:
    def test_lower_complexity_flagged_informational(self):
        f = facility_oversight_context(_base(possesses_classified_it_systems_onsite=False, stores_classified_material_onsite=False))
        assert f.matched is True
        assert f.points == 0
        assert "NAESOC" in f.explanation

    def test_higher_complexity_not_flagged(self):
        f = facility_oversight_context(_base(possesses_classified_it_systems_onsite=True))
        assert f.matched is False

    def test_never_contributes_points_either_way(self):
        for it, material in [(True, True), (False, False), (True, False)]:
            f = facility_oversight_context(_base(possesses_classified_it_systems_onsite=it, stores_classified_material_onsite=material))
            assert f.points == 0


class TestAllIndicatorsHaveCitations:
    def test_every_indicator_cites_a_real_source(self):
        inputs = _base()
        for fn in ALL_INDICATORS:
            finding = fn(inputs)
            assert finding.citation.strip(), f"{fn.__name__} has no citation"

    def test_every_indicator_id_is_unique(self):
        inputs = _base()
        ids = [fn(inputs).indicator_id for fn in ALL_INDICATORS]
        assert len(ids) == len(set(ids))
