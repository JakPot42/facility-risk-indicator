"""End-to-end CLI tests. No network calls (DEMO_MODE=True is the default)."""
from __future__ import annotations

import json
import os
import sys

from click.testing import CliRunner

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import cli


def _run(*args):
    runner = CliRunner()
    return runner.invoke(cli, args)


def _flat(text: str) -> str:
    stripped = text.replace("|", " ").replace("+", " ").replace("-", " ")
    return " ".join(stripped.split())


class TestScopeDisclaimerAlwaysPresent:
    def test_on_assess(self):
        result = _run("assess", "--months-since-self-inspection", "3", "--open-violations", "0")
        assert result.exit_code == 0
        assert "NOT surveil" in _flat(result.output)

    def test_on_demo(self):
        result = _run("demo")
        assert result.exit_code == 0
        assert "NOT surveil" in _flat(result.output)

    def test_on_indicators(self):
        result = _run("indicators")
        assert result.exit_code == 0
        assert "NOT surveil" in _flat(result.output)

    def test_group_help_mentions_scope(self):
        result = _run("--help")
        assert "NOT surveil" in _flat(result.output)


class TestAssessCommand:
    def test_clean_facility_low_score(self):
        result = _run(
            "assess", "--months-since-self-inspection", "1", "--open-violations", "0",
            "--fso-tenure-months", "24",
        )
        assert result.exit_code == 0
        assert "LOW" in result.output

    def test_flagged_facility_shows_findings(self):
        result = _run(
            "assess", "--months-since-self-inspection", "24", "--no-self-inspection-certified",
            "--open-violations", "8", "--violation-category", "physical_loss:8",
        )
        assert result.exit_code == 0
        assert "Self-Inspection" in result.output

    def test_unknown_violation_category_rejected(self):
        result = _run("assess", "--months-since-self-inspection", "1", "--open-violations", "0", "--violation-category", "not_a_real_category:5")
        assert result.exit_code != 0

    def test_json_output_is_valid_json(self):
        result = _run("assess", "--months-since-self-inspection", "1", "--open-violations", "0", "--format", "json")
        data = json.loads(result.output)
        assert "score" in data
        assert "findings" in data

    def test_fso_omitted_means_vacant(self):
        result = _run("assess", "--months-since-self-inspection", "1", "--open-violations", "0", "--format", "json")
        data = json.loads(result.output)
        fso_finding = next(f for f in data["findings"] if f["indicator_id"] == "fso_position_status")
        assert fso_finding["matched"] is True
        assert "Vacant" in fso_finding["label"]


class TestDemoCommand:
    def test_runs_all_four_scenarios(self):
        result = _run("demo")
        assert result.exit_code == 0
        assert "Cedar Ridge" in result.output
        assert "Harlow Defense" in result.output
        assert "Ashford Precision" in result.output
        assert "Bright Path" in result.output

    def test_shows_differentiated_tiers(self):
        result = _run("demo")
        assert "LOW" in result.output
        assert "CRITICAL" in result.output


class TestIndicatorsCommand:
    def test_lists_all_indicator_ids(self):
        result = _run("indicators")
        for indicator_id in (
            "self_inspection_overdue", "self_inspection_certification_missing",
            "fso_position_status", "violation_count_outlier",
            "vulnerability_count_outlier", "dcsa_review_overdue",
            "violation_category_concentration", "facility_oversight_context",
        ):
            assert indicator_id in result.output

    def test_shows_real_citations(self):
        result = _run("indicators")
        flat = _flat(result.output)
        assert "117.7" in flat
        assert "117.12" in flat
        assert "GAO" in flat
