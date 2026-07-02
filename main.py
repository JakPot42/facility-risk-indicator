"""Cleared Facility Institutional Risk Indicator CLI.

Assesses INSTITUTIONAL / FACILITY-LEVEL security program patterns only.
Never surveils, scores, or assesses any individual person. See
config.SCOPE_DISCLAIMER, printed on every command.
"""
from __future__ import annotations

import os
import sys

import click

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claude_assessor import generate_narrative
from config import DEMO_MODE, GAO_VIOLATION_CATEGORY_MIX
from dashboard import (
    console,
    print_banner,
    print_citations,
    print_findings,
    print_indicator_library,
    print_json,
    print_narrative,
    print_score,
)
from indicators import ALL_INDICATORS
from models import FacilityInputs
from risk_engine import assess_facility


def _parse_categories(pairs: tuple[str, ...]) -> dict[str, int]:
    categories: dict[str, int] = {}
    for pair in pairs:
        if ":" not in pair:
            raise click.BadParameter(f"Expected category:count, got {pair!r}")
        category, count = pair.rsplit(":", 1)
        if category not in GAO_VIOLATION_CATEGORY_MIX:
            valid = ", ".join(sorted(GAO_VIOLATION_CATEGORY_MIX))
            raise click.BadParameter(f"Unknown category {category!r}. Valid: {valid}")
        categories[category] = int(count)
    return categories


@click.group()
def cli() -> None:
    """
    Cleared Facility Institutional Risk Indicator: a self-assessment tool
    for cleared facility security managers.

    \b
    Assesses INSTITUTIONAL / FACILITY-LEVEL security program patterns
    only -- violation counts, inspection cadence, certification status.
    It does NOT surveil, score, or assess any individual person's
    behavior, psychology, finances, or personal circumstances. It is NOT
    predictive of specific incidents. Every indicator cites a real,
    checkable source (NISPOM / 32 CFR Part 117, GAO-26-107861).
    """


@cli.command()
@click.option("--label", default="Unlabeled facility", help="A facility identifier of your choosing (never a person's name).")
@click.option("--months-since-self-inspection", type=int, required=True)
@click.option("--self-inspection-certified/--no-self-inspection-certified", default=True)
@click.option("--fso-tenure-months", type=int, default=None, help="Months since the current FSO was appointed. Omit if the position is vacant.")
@click.option("--open-violations", type=int, required=True)
@click.option("--violation-category", "violation_categories", multiple=True, help="category:count, e.g. data_spill:2. Repeatable.")
@click.option("--open-vulnerabilities", type=int, default=0)
@click.option("--months-since-dcsa-review", type=int, default=None)
@click.option("--has-classified-it/--no-classified-it", default=False)
@click.option("--stores-classified-material/--no-classified-material", default=False)
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table")
def assess(
    label, months_since_self_inspection, self_inspection_certified,
    fso_tenure_months, open_violations, violation_categories,
    open_vulnerabilities, months_since_dcsa_review,
    has_classified_it, stores_classified_material, fmt,
) -> None:
    """Assess one facility from institutional metrics you supply."""
    if fmt == "table":
        print_banner()

    inputs = FacilityInputs(
        facility_label=label,
        months_since_last_self_inspection=months_since_self_inspection,
        self_inspection_certified_current_year=self_inspection_certified,
        fso_tenure_months=fso_tenure_months,
        open_violation_count=open_violations,
        violation_categories=_parse_categories(violation_categories),
        open_vulnerability_count=open_vulnerabilities,
        months_since_last_dcsa_review=months_since_dcsa_review,
        possesses_classified_it_systems_onsite=has_classified_it,
        stores_classified_material_onsite=stores_classified_material,
    )
    result = assess_facility(inputs)
    narrative = generate_narrative(result)

    if fmt == "json":
        print_json({
            "facility_label": result.facility_label,
            "score": result.score,
            "tier": result.tier,
            "findings": [f.__dict__ for f in result.findings],
            "narrative": narrative,
        })
    else:
        print_findings(result)
        print_citations(result)
        print_score(result)
        print_narrative(narrative)
        if DEMO_MODE:
            console.print("[dim]DEMO_MODE=True -- narrative uses a deterministic template, not a live Claude call.[/dim]")


@cli.command()
def demo() -> None:
    """Run all four bundled fictional demo facilities, spanning LOW through HIGH."""
    print_banner()
    import seed_data

    for key in ("well_run", "naesoc_tier", "moderate_risk", "high_risk"):
        inputs = seed_data.DEMO_FACILITIES[key]
        result = assess_facility(inputs)
        narrative = generate_narrative(result)
        print_findings(result)
        print_citations(result)
        print_score(result)
        print_narrative(narrative)

    if DEMO_MODE:
        console.print("[dim]DEMO_MODE=True -- narratives use a deterministic template, not a live Claude call.[/dim]")


@cli.command(name="indicators")
def show_indicators() -> None:
    """List every indicator in the library and its citation -- full
    transparency on what this tool checks and where each rule comes from."""
    print_banner()
    print_indicator_library(ALL_INDICATORS)


if __name__ == "__main__":
    cli()
