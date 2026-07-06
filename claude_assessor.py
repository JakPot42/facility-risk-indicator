"""claude_assessor.py — plain-language narrative of an already-computed
assessment. Claude's role is narrow: describe which documented
institutional patterns matched and weave together the (already-defined,
cited) remediation steps into readable prose. It never decides which
indicators fire, never assigns severity or points, and never mentions
any individual person -- there is no field in AssessmentResult it could
even reference that would let it. DEMO_MODE (default) uses a
deterministic template, zero API keys needed.
"""
from __future__ import annotations

from claude_client import call_claude
from config import CLAUDE_MODEL, DEMO_MODE
from models import AssessmentResult

_NOT_PREDICTIVE_NOTE = (
    "This assessment reflects documented institutional risk patterns "
    "only and is NOT predictive of any specific incident."
)


def _demo_narrative(result: AssessmentResult) -> str:
    matched = [f for f in result.findings if f.matched]
    lines = [
        f"Facility risk assessment: {result.facility_label}",
        f"Score: {result.score}/100 ({result.tier})",
        "",
    ]
    if not matched:
        lines.append("No documented institutional risk patterns matched this facility's inputs.")
    else:
        lines.append(f"{len(matched)} documented institutional risk pattern(s) matched:")
        for f in matched:
            lines.append(f"- [{f.severity}] {f.label}: {f.explanation}")
        lines.append("")
        lines.append("Remediation steps:")
        for f in matched:
            if f.remediation:
                lines.append(f"- {f.label}: {f.remediation}")
    lines.append("")
    lines.append(_NOT_PREDICTIVE_NOTE)
    return "\n".join(lines)


_SYSTEM_PROMPT = """\
You write a plain-language facility security program assessment for a \
cleared-facility security manager. You are given a list of already-\
computed institutional findings (facility-level operational facts only \
-- violation counts, inspection cadence, certification status) with \
their severity, citation, and remediation step already determined. Do \
NOT invent a new finding, re-score anything, or discuss any individual \
person -- there is no individual-level data in what you're given. \
Summarize which documented patterns matched and weave in the provided \
remediation steps. End with the sentence: "This assessment reflects \
documented institutional risk patterns only and is NOT predictive of \
any specific incident." Plain prose, no markdown headers.
"""


def _claude_narrative(result: AssessmentResult) -> str:
    try:
        matched = [f for f in result.findings if f.matched]
        prompt = (
            f"Facility: {result.facility_label}\n"
            f"Score: {result.score}/100, tier {result.tier}\n"
            f"Matched findings: "
            f"{[(f.label, f.severity, f.explanation, f.citation, f.remediation) for f in matched]}\n"
        )
        return call_claude(
            [{"role": "user", "content": prompt}],
            system=_SYSTEM_PROMPT,
            max_tokens=600,
            model=CLAUDE_MODEL,
        )
    except Exception:
        # Same doctrine as every Claude call site in this portfolio: catch
        # Exception broadly (call_claude() itself wraps SDK failures into
        # ClaudeCallError, but this stays a broad except -- this CLI must
        # never crash on a Claude failure, only narrate less), fall back
        # rather than crash.
        return _demo_narrative(result)


def generate_narrative(result: AssessmentResult) -> str:
    return _demo_narrative(result) if DEMO_MODE else _claude_narrative(result)
