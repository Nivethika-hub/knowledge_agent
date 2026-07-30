"""Coordinator agent for planning and consolidating the specialist workflow."""

from __future__ import annotations

import logging
from statistics import fmean
from typing import Any

from app.agents.agent_state import AgentName, AgentState, build_processing_log, utc_now

logger = logging.getLogger(__name__)

DOCUMENTATION_TERMS = (
    "document",
    "documentation",
    "adr",
    "architecture decision record",
    "meeting summary",
    "release notes",
    "technical summary",
    "feature summary",
)
CORE_AGENTS: list[AgentName] = ["context", "timeline", "reasoning", "citation"]


def documentation_requested(question: str) -> bool:
    """Classify documentation requests deterministically and transparently."""
    normalised = question.lower()
    return any(term in normalised for term in DOCUMENTATION_TERMS)


def _confidence(state: AgentState) -> float:
    nodes = state.get("retrieved_knowledge_nodes", [])
    if not nodes:
        return 0.0
    similarity = fmean(float(node.get("similarity", 0.0)) for node in nodes)
    citation_coverage = min(len(state.get("citations", [])) / len(nodes), 1.0)
    return round(min((similarity * 0.8) + (citation_coverage * 0.2), 1.0), 2)


def _final_answer(state: AgentState) -> str:
    reasoning = state.get("reasoning", {})
    if not state.get("retrieved_knowledge_nodes"):
        return (
            "I could not find sufficiently relevant knowledge nodes to answer "
            "this question. Try naming the feature, decision, or project involved."
        )
    explanation = str(reasoning.get("explanation", "")).strip()
    decision = str(reasoning.get("decision", "")).strip()
    parts = [part for part in (decision, explanation) if part]
    return "\n\n".join(parts) or "The retrieved evidence did not contain an answer."


def coordinator_agent(state: AgentState) -> dict[str, Any]:
    """Plan the first pass or consolidate the completed workflow's outputs."""
    started_at = utc_now()
    question = state.get("question", "").strip()
    if not state.get("requested_agents"):
        needs_docs = documentation_requested(question)
        requested_agents = list(CORE_AGENTS)
        if needs_docs:
            requested_agents.append("documentation")
        intent = "documentation" if needs_docs else "question"
        message = f"Planned {intent} workflow with {len(requested_agents)} specialist agent(s)."
        logger.info("Coordinator agent: %s", message)
        return {
            "intent": intent,
            "requested_agents": requested_agents,
            "processing_logs": [
                build_processing_log("coordinator", "completed", started_at, message)
            ],
        }

    confidence = _confidence(state)
    message = "Consolidated specialist outputs into the final response."
    logger.info("Coordinator agent: %s", message)
    return {
        "final_answer": _final_answer(state),
        "confidence": confidence,
        "processing_logs": [
            build_processing_log("coordinator", "completed", started_at, message)
        ],
    }
