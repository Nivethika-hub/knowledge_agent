"""Grounded reasoning agent for evidence-based organizational answers."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.agents.agent_state import AgentState, build_processing_log, utc_now
from app.rag.llm_service import call_llm_with_system

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the reasoning component of an enterprise knowledge
system. Use only the supplied evidence. Do not add facts, infer unstated
motives, or cite sources not included in the evidence. Return only valid JSON
with string keys: decision, reason, impact, trade_offs, explanation. Use an
empty string when the evidence does not support a field."""


def _fallback_reasoning(nodes: list[dict[str, Any]]) -> dict[str, str]:
    """Create a factual answer when the LLM cannot be used."""
    decisions = [node.get("decision", "").strip() for node in nodes]
    decisions = [decision for decision in decisions if decision]
    documents = [node.get("document", "").strip() for node in nodes]
    first_document = next((document for document in documents if document), "")
    decision = decisions[0] if decisions else "No explicit decision was retrieved."
    return {
        "decision": decision,
        "reason": "See the retrieved evidence for the documented rationale.",
        "impact": "Not established by the retrieved evidence.",
        "trade_offs": "Not established by the retrieved evidence.",
        "explanation": first_document or "No relevant evidence was retrieved.",
    }


def _parse_reasoning(response: str) -> dict[str, str]:
    """Validate the LLM response and retain the fixed public reasoning schema."""
    # Models commonly wrap an otherwise valid JSON object in a Markdown code
    # fence despite the prompt's "valid JSON only" instruction. Accept that
    # presentation format while keeping schema validation strict.
    payload = response.strip()
    if payload.startswith("```"):
        lines = payload.splitlines()
        if lines and lines[0].lstrip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        payload = "\n".join(lines).strip()

    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("LLM response was not a JSON object.")
    keys = ("decision", "reason", "impact", "trade_offs", "explanation")
    return {key: str(parsed.get(key, "")).strip() for key in keys}


def reasoning_agent(state: AgentState) -> dict[str, Any]:
    """Explain evidence without expanding beyond the retrieved knowledge nodes."""
    started_at = utc_now()
    nodes = state.get("retrieved_knowledge_nodes", [])
    if not nodes:
        message = "Reasoning skipped because no relevant evidence was retrieved."
        return {
            "reasoning": _fallback_reasoning([]),
            "processing_logs": [
                build_processing_log("reasoning", "skipped", started_at, message)
            ],
        }

    evidence = state.get("evidence", [])
    prompt = json.dumps(
        {"question": state.get("question", ""), "evidence": evidence},
        ensure_ascii=False,
        indent=2,
    )
    try:
        response = call_llm_with_system(
            SYSTEM_PROMPT,
            prompt,
            temperature=0.0,
            max_tokens=700,
        )
        reasoning = _parse_reasoning(response)
        message = "Generated a grounded reasoning summary."
        status = "completed"
    except Exception as exc:
        logger.warning("Reasoning agent fell back to deterministic summary: %s", exc)
        reasoning = _fallback_reasoning(nodes)
        message = f"LLM reasoning unavailable; used evidence-only fallback: {exc}"
        status = "failed"

    updates: dict[str, Any] = {
        "reasoning": reasoning,
        "processing_logs": [
            build_processing_log("reasoning", status, started_at, message)
        ],
    }
    if status == "failed":
        updates["errors"] = [message]
    return updates
