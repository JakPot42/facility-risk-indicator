"""Rich terminal dashboard — ASCII-safe for Windows cp1252 console.
Every Table AND Panel uses box.ASCII2 -- a Panel with Rich's default
Unicode box style crashes with UnicodeEncodeError on a real cp1252
console (learned the hard way in a previous portfolio build)."""
from __future__ import annotations

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import SCOPE_DISCLAIMER
from models import AssessmentResult

console = Console(width=110)

TIER_COLORS = {"LOW": "green", "MODERATE": "yellow", "HIGH": "red", "CRITICAL": "bold red"}
SEVERITY_COLORS = {"INFORMATIONAL": "dim", "MODERATE": "yellow", "HIGH": "red"}

_BANNER = "[bold cyan]Cleared Facility Institutional Risk Indicator[/bold cyan]  [dim]v1.0[/dim]"


def print_banner() -> None:
    console.print()
    console.print(_BANNER)
    console.print(Panel(SCOPE_DISCLAIMER, box=box.ASCII2, border_style="yellow", title="[bold yellow]Scope[/bold yellow]"))


def print_findings(result: AssessmentResult) -> None:
    console.rule(f"[bold]{result.facility_label}[/bold]")
    t = Table(box=box.ASCII2)
    t.add_column("Matched")
    t.add_column("Indicator", overflow="fold")
    t.add_column("Severity")
    t.add_column("Explanation", overflow="fold")
    for f in result.findings:
        matched_label = "[bold]YES[/bold]" if f.matched else "no"
        color = SEVERITY_COLORS.get(f.severity, "white")
        t.add_row(matched_label, f.label, f"[{color}]{f.severity}[/{color}]", f.explanation)
    console.print(t)


def print_citations(result: AssessmentResult) -> None:
    console.rule("[bold]Citations[/bold]")
    seen = set()
    for f in result.findings:
        if f.citation in seen:
            continue
        seen.add(f.citation)
        console.print(f"  [dim]{f.citation}[/dim]")
    console.print()


def print_score(result: AssessmentResult) -> None:
    color = TIER_COLORS.get(result.tier, "white")
    console.print(Panel(
        f"Score: [{color}]{result.score}/100[/{color}]   Tier: [{color}]{result.tier}[/{color}]\n"
        f"[dim]This score reflects documented institutional risk patterns only "
        f"and is NOT predictive of any specific incident.[/dim]",
        box=box.ASCII2, title="[bold]Institutional Risk Score[/bold]", border_style=color,
    ))


def print_narrative(text: str) -> None:
    console.rule("[bold]Plain-Language Assessment[/bold]")
    console.print(text)
    console.print()


def print_indicator_library(indicator_fns) -> None:
    console.rule("[bold]Indicator Library[/bold]")
    from models import FacilityInputs
    probe = FacilityInputs(
        facility_label="(library listing)", months_since_last_self_inspection=0,
        self_inspection_certified_current_year=True, fso_tenure_months=99,
        open_violation_count=0, violation_categories={},
    )
    for fn in indicator_fns:
        finding = fn(probe)
        console.print(f"[bold]{finding.label}[/bold]  [dim]({finding.indicator_id})[/dim]")
        console.print(f"  {finding.citation}")
        console.print()


def print_json(data) -> None:
    import json
    console.print_json(json.dumps(data))
