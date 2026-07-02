"""Tests for models.py — including a direct structural regression test
that FacilityInputs cannot represent an identifiable individual. This
test is meant to fail loudly if a future edit ever adds a name/ID/date
field to the dataclass -- the guarantee is structural, not a comment."""
from __future__ import annotations

import dataclasses
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import AssessmentResult, FacilityInputs, Finding

_FORBIDDEN_FIELD_SUBSTRINGS = [
    "name", "employee", "person", "individual", "appointment_date",
    "birth", "ssn", "email", "phone",
]


class TestFacilityInputsHasNoIndividualLevelFields:
    def test_no_forbidden_substrings_in_field_names(self):
        field_names = [f.name for f in dataclasses.fields(FacilityInputs)]
        for field_name in field_names:
            for forbidden in _FORBIDDEN_FIELD_SUBSTRINGS:
                assert forbidden not in field_name.lower(), (
                    f"FacilityInputs.{field_name} contains {forbidden!r} -- "
                    f"this dataclass must never be able to represent an "
                    f"identifiable individual."
                )

    def test_fso_field_is_bare_integer_or_none_only(self):
        fso_field = next(f for f in dataclasses.fields(FacilityInputs) if f.name == "fso_tenure_months")
        assert fso_field.type == "int | None"

    def test_no_free_text_fields_besides_the_facility_label(self):
        # facility_label is a manager-chosen reference string (e.g. "Building 4"),
        # explicitly documented as never a person's name -- every other field
        # must be numeric or boolean, not free text that could smuggle in
        # individual-level detail.
        for f in dataclasses.fields(FacilityInputs):
            if f.name in ("facility_label", "violation_categories"):
                continue
            assert f.type in ("int", "int | None", "bool"), f"{f.name} has type {f.type!r}, expected numeric/boolean"


class TestFinding:
    def test_all_fields_present(self):
        finding = Finding(
            indicator_id="x", label="X", matched=True, severity="HIGH",
            points=10, explanation="e", citation="c", remediation="r",
        )
        assert finding.matched is True


class TestAssessmentResult:
    def test_holds_findings_list(self):
        result = AssessmentResult(facility_label="Test", findings=[], score=0, tier="LOW")
        assert result.findings == []
