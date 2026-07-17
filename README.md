# Cleared Facility Institutional Risk Indicator

> **This tool assesses INSTITUTIONAL / FACILITY-LEVEL security program
> patterns only.** It does NOT surveil, score, or assess any individual
> person's behavior, psychology, finances, foreign contacts, or any
> other personal circumstance. "This facility has 14 unresolved security
> violations pending" is institutional data this tool uses. "This
> employee shows financial stress indicators" is individual data this
> tool **never** touches, collects, or infers. It is **not predictive**
> of any specific incident — it maps facility inputs against documented
> institutional risk patterns from public PERSEREC-adjacent, NISPOM, and
> GAO research, with citations, full stop.


---

## What It Does

A self-assessment tool for cleared facility security managers. The
manager inputs facility-level operational metrics — self-inspection
cadence, open violation count, DCSA review recency, and similar — and a
deterministic scoring engine maps those against a cited library of
institutional risk indicators drawn from NISPOM (32 CFR Part 117) and a
2026 GAO report on DCSA industrial security oversight. Claude then writes
a plain-language summary of which documented patterns matched, weaving in
the (already-defined, cited) remediation steps — it never decides which
indicators fire, never assigns severity or points, and never mentions any
individual, because there is no individual-level data anywhere in the
pipeline for it to reference.

---

## The Institutional/Individual Line — How It's Enforced, Not Just Stated

This is the most important discipline in this build, and it's enforced
structurally, not just in prose:

- `models.py`'s `FacilityInputs` dataclass has **no name field, no
  employee ID, no free-text field of any kind** besides a manager-chosen
  facility label (e.g. "Building 4" — explicitly documented as never a
  person's name). Every other field is a plain integer, boolean, or a
  category→count dict. `tests/test_models.py` asserts this directly: it
  scans every field name for forbidden substrings ("name", "employee",
  "person", "appointment_date", etc.) and asserts every non-label field's
  type is numeric or boolean — a future edit that tried to add individual-
  level data would fail this test, not just violate a comment.
- **FSO tenure — the one input that sits closest to the line.** The
  build spec named "FSO tenure" as an input. It maps to a real regulatory
  fact (32 CFR 117.12(d): a newly appointed FSO must complete required
  training within 6 months), so it's legitimately an institutional
  program-continuity metric — but it's *about* a role a specific person
  occupies, which is close enough to the line that this was raised as an
  explicit decision point rather than guessed at. Resolution: the data
  model stores **only** `fso_tenure_months: int | None` (months since
  appointment, computed by the manager before typing it in) — never a
  name, an appointment date, or anything else that could be joined back
  to a specific identifiable person. Every output string this metric
  produces talks about "the FSO position" or "the role," never "the
  FSO" as a stand-in for a named individual — see `indicators.py`'s
  `fso_position_status()` and the regression test that greps its output
  for exactly that framing.
- Claude (`claude_assessor.py`) is handed a list of already-computed,
  already-scored `Finding` objects and nothing else — there is no field
  in that structure it could use to say anything about a person even if
  it tried. `tests/test_claude_assessor.py` asserts the generated
  narrative never contains individual-level phrasing.

---

## Cited Indicator Library

Real, checkable sources — no invented thresholds. Run `python main.py
indicators` to see the full library with citations printed live.

| Indicator | Source |
|---|---|
| Self-inspection overdue (>12mo / >24mo) | 32 CFR 117.7(a) — formal self-inspection required at least annually |
| Self-inspection certification missing | 32 CFR 117.7 — SMO must annually certify in writing that self-inspection was conducted, KMP briefed, corrective action taken |
| FSO position vacant / within training window | 32 CFR 117.12(d) — FSO training must complete within 6 months of appointment |
| Open violation count outlier | GAO-26-107861 (April 24, 2026) — DCSA documented 815 violations across 4,600+ FY2025 security reviews (~0.18/review national average) |
| Open vulnerability count outlier | GAO-26-107861 — 1,032 open vulnerabilities documented nationally as of September 2025 |
| DCSA review significantly overdue | GAO-26-107861 — DCSA completed under 40% of required inspections in FY2025; resourced for only 25-30% of cleared industrial base coverage per 2023 findings |
| Violation category concentration | GAO-26-107861's FY2025 violation category mix (60% data spill, 11.5% improper storage, 6.5% access breach, 6.3% physical loss, 5.6% improper physical transfer) |
| Facility oversight complexity context (informational only) | GAO-26-107861 — describes DCSA's NAESOC (National Access Elsewhere Security Oversight Center, est. 2019) tier for facilities without on-site classified IT/material |

**GAO-26-107861**, "Industrial Security: Improved Risk Management and
Stakeholder Engagement Needed to Help DOD Address Mission Gaps" (U.S.
Government Accountability Office, April 24, 2026) — researched live for
this build since it postdates any training-data cutoff.

---

## How Thresholds Were Chosen

Where GAO/NISPOM publish an exact requirement (self-inspection at least
annually, FSO training within 6 months), that number is used directly.
Where GAO documents a national aggregate but not a per-facility
distribution (e.g. "815 violations, 4,600+ reviews" doesn't tell you the
25th/75th percentile of violations-per-facility), this tool uses a round,
clearly-outlying multiple of the national average rather than a
fabricated precise percentile — disclosed here and in `config.py`
comments, not hidden. Example: the "violation count outlier" thresholds
(3 = MODERATE, 6 = HIGH) are roughly 17x and 34x the FY2025 national
per-review average of ~0.18 — a facility hitting either is a genuine
outlier against the documented baseline, even without a published
percentile to compare against exactly.

---

## Architecture

```
config.py              Cited indicators, national baselines (GAO-26-107861), NISPOM citations, thresholds -- no logic
models.py                FacilityInputs / Finding / AssessmentResult -- structurally incapable of individual-level data
indicators.py              Deterministic rule engine -- one function per cited indicator
risk_engine.py               Aggregates Findings into a score (0-100) and LOW/MODERATE/HIGH/CRITICAL tier
claude_assessor.py             Plain-language narrative of already-computed findings (DEMO_MODE template or live Claude)
seed_data.py                    Four fictional demo facility scenarios spanning LOW-CRITICAL
dashboard.py                     Rich terminal rendering (ASCII-safe -- Table AND Panel)
main.py                           Click CLI
```

---

## Quick Start

```bash
git clone https://github.com/JakPot42/facility-risk-indicator.git
cd facility-risk-indicator
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\python main.py demo
```

## Commands

```bash
python main.py demo         # four fictional demo facilities, LOW through CRITICAL
python main.py indicators   # full cited indicator library, with citations printed live
python main.py assess --months-since-self-inspection 3 --open-violations 0 \
    --fso-tenure-months 24 --has-classified-it --stores-classified-material
python main.py assess --months-since-self-inspection 24 --no-self-inspection-certified \
    --open-violations 8 --violation-category physical_loss:8 --format json
```

`assess` never asks for a name, an employee ID, or any personal detail —
every option is a facility-level count, a duration in months, or a
boolean. DEMO_MODE=True (default) needs zero API keys; the narrative uses
a deterministic template. Set `DEMO_MODE=False` with a valid
`ANTHROPIC_API_KEY` for a live Claude narrative — it's handed the exact
same already-computed, individual-data-free findings either way.

---

## Tests

```bash
python -m pytest -q
# 62 passed
```

Covers: a direct structural test that `FacilityInputs` cannot represent
an identifiable individual (scans field names and types, not just
behavior), every indicator's boundary conditions and citations, the FSO
position indicator's careful role-vs-person framing, deterministic risk
scoring and tier boundaries, the Claude narrative generator (including a
check that it never uses individual-level phrasing), the four demo
scenarios, and end-to-end CLI commands.

---

## Honest Limitations

- Thresholds not directly published by GAO/NISPOM are disclosed
  simplifications (round multiples of a national average), not precise
  statistical cutoffs — see "How Thresholds Were Chosen" above.
- The violation-category-concentration check compares a facility's own
  mix against one national snapshot (GAO-26-107861, FY2025) — it isn't a
  longitudinal or statistically-tested comparison.
- This tool cannot verify that a manager's inputs are accurate; it only
  scores what's entered.
- This is explicitly not predictive of any specific incident, and not a
  substitute for an actual DCSA security review or self-inspection.

---

*Institutional/facility-level patterns only. Never individual behavior.
Not predictive of specific incidents. Every citation traces to a real,
dated, public source.*
