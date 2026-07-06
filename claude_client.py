"""
Canonical Claude API call wrapper for the Cleared Facility Suite cluster
(Phase 6, Cluster 3).

Every consuming project should call `call_claude()` instead of constructing
its own anthropic.Anthropic client and its own try/except around
messages.create(). This exists because two real bugs were found and fixed
across this cluster's own source projects before this library existed:
ato_accelerator's categorize_system() had an unreachable
`except json.JSONDecodeError` clause placed AFTER a catch-all
`except Exception` (JSONDecodeError is itself an Exception subclass, so it
could never fire -- caught by that project's own test suite, which was
failing until fixed), and clearance_advisor's claude_advisor.py had NO
exception handling at all around either of its two Claude call sites.
Routing every call through one wrapper makes both failure modes
structurally impossible to reintroduce.

The Anthropic SDK raises a bare TypeError (not anthropic.APIError) when
api_key is empty or malformed -- catching Exception broadly, not
anthropic.APIError specifically, is deliberate and matches the portfolio-
wide fix already applied elsewhere.

Distributed here (Step 3, consistency pass, not a fix) from
cleared-facility-suite's shared/claude_client.py -- facility_risk_indicator's
own claude_assessor.py already caught broad Exception and fell back to a
deterministic narrative correctly; this only centralizes the call site
itself, same as the other CLI tools in this cluster.
"""
from __future__ import annotations

import os

import anthropic

CLAUDE_MODEL = "claude-haiku-4-5-20251001"


class ClaudeCallError(Exception):
    """Raised for any Claude API failure -- missing key, network error,
    rate limit, malformed response, etc. Wraps the original exception."""


def call_claude(
    messages: list[dict],
    *,
    system: str | None = None,
    max_tokens: int = 1024,
    model: str = CLAUDE_MODEL,
    api_key: str | None = None,
) -> str:
    """
    Call Claude and return the response text (content[0].text, stripped).

    Raises ClaudeCallError -- never a bare SDK exception -- on any failure.
    Callers that need structured output (JSON, etc.) parse the returned
    string themselves; this wrapper only guarantees the call itself either
    succeeds or raises ClaudeCallError, nothing more.
    """
    key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise ClaudeCallError(
            "ANTHROPIC_API_KEY not set. Set it in the environment or pass api_key= explicitly."
        )

    try:
        client = anthropic.Anthropic(api_key=key)
        kwargs: dict = {"model": model, "max_tokens": max_tokens, "messages": messages}
        if system is not None:
            kwargs["system"] = system
        response = client.messages.create(**kwargs)
    except Exception as exc:
        raise ClaudeCallError(f"Claude API error: {exc}") from exc

    return response.content[0].text.strip()
