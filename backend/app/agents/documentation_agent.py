"""Agent that produces evidence-grounded Markdown documentation."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.agents.agent_state import AgentState, build_processing_log, utc_now
from app.rag.llm_service import call_llm_with_system

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You create concise enterprise documentation. Use only the
provided evidence; explicitly mark unsupported details as 'Not established by
the retrieved evidence.' Return only valid JSON with the keys adr,
meeting_summary, and release_notes. Each value must be Markdown."""


def _evidence_lines(state: AgentState) -> str:
    return "\n".join(
        f"- {item.get('feature', 'Unknown')}: {item.get('content', '')}"
        for item in state.get("evidence", [])
    ) or "- No relevant evidence was retrieved."


def _fallback_documentation(state: AgentState) -> dict[str, str]:
    """Create useful, source-bound documentation without an LLM dependency."""
    subject = state.get("question", "Requested feature")
    reasoning = state.get("reasoning", {})
    decision = reasoning.get("decision", "No explicit decision was retrieved.")
    evidence = _evidence_lines(state)
    timeline = state.get("timeline", [])
    timeline_lines = "\n".join(
        f"- {event.get('timestamp', 'Unknown time')} — "
        f"{event.get('platform', 'Unknown')}: {event.get('title', '')}"
        for event in timeline
    ) or "- No timestamped events were retrieved."
    return {
        "adr": (
            f"# Architecture Decision Record: {subject}\n\n"
            "## Decision\n\n"
            f"{decision}\n\n"
            "## Rationale\n\n"
            f"{reasoning.get('reason', 'Not established by the retrieved evidence.')}\n\n"
            "## Evidence\n\n"
            f"{evidence}\n"
        ),
        "meeting_summary": (
            f"# Meeting Summary: {subject}\n\n"
            "## Key outcome\n\n"
            f"{decision}\n\n"
            "## Recorded timeline\n\n"
            f"{timeline_lines}\n"
        ),
        "release_notes": (
            f"# Release Notes: {subject}\n\n"
            "## Summary\n\n"
            f"{reasoning.get('explanation', 'Not established by the retrieved evidence.')}\n\n"
            "## Impact\n\n"
            f"{reasoning.get('impact', 'Not established by the retrieved evidence.')}\n"
        ),
    }


def _parse_documentation(response: str) -> dict[str, str]:
    parsed = json.loads(response)
    if not isinstance(parsed, dict):
        raise ValueError("LLM response was not a JSON object.")
    required = ("adr", "meeting_summary", "release_notes")
    if any(not str(parsed.get(key, "")).strip() for key in required):
        raise ValueError("LLM response did not contain every required document.")
    return {key: str(parsed[key]).strip() for key in required}


def documentation_agent(state: AgentState) -> dict[str, Any]:
    """Generate the requested documentation set from already retrieved evidence."""
    started_at = utc_now()
    payload = json.dumps(
        {
            "subject": state.get("question", ""),
            "reasoning": state.get("reasoning", {}),
            "timeline": state.get("timeline", []),
            "evidence": state.get("evidence", []),
        },
        ensure_ascii=False,
    )
    try:
        documentation = _parse_documentation(
            call_llm_with_system(SYSTEM_PROMPT, payload, temperature=0.0, max_tokens=1400)
        )
        message = "Generated the requested documentation set."
        status = "completed"
    except Exception as exc:
        logger.warning("Documentation agent used fallback: %s", exc)
        documentation = _fallback_documentation(state)
        message = f"LLM documentation unavailable; used evidence-only fallback: {exc}"
        status = "failed"

    updates: dict[str, Any] = {
        "generated_documentation": documentation,
        "processing_logs": [
            build_processing_log("documentation", status, started_at, message)
        ],
    }
    if status == "failed":
        updates["errors"] = [message]
    return updates
