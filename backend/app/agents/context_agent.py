"""Evidence-grounded knowledge retrieval agent."""

from __future__ import annotations

import logging
from typing import Any

from app.agents.agent_state import AgentState, build_processing_log, utc_now
from app.rag.rag_pipeline import retrieve_context

logger = logging.getLogger(__name__)

DEFAULT_TOP_K = 6
MIN_SIMILARITY = 0.25


def _normalise_node(node: dict[str, Any]) -> dict[str, Any]:
    """Return the fields downstream agents need in a stable format."""
    return {
        "feature": str(node.get("feature", "")),
        "similarity": float(node.get("similarity", 0.0)),
        "decision": str(node.get("decision", "")),
        "participants": list(node.get("participants", [])),
        "document": str(node.get("document", "")),
    }


def context_agent(state: AgentState) -> dict[str, Any]:
    """Retrieve and rank relevant knowledge nodes for the user's question.

    This agent deliberately does not call an LLM: it preserves deterministic
    retrieval, reuses the already-initialised embedding and ChromaDB clients,
    and supplies only evidence-bearing nodes to later agents.
    """
    started_at = utc_now()
    question = state.get("question", "").strip()

    if not question:
        message = "A question is required before retrieval can run."
        return {
            "retrieved_knowledge_nodes": [],
            "evidence": [],
            "errors": [message],
            "processing_logs": [
                build_processing_log("context", "failed", started_at, message)
            ],
        }

    try:
        retrieved = retrieve_context(question, top_k=DEFAULT_TOP_K)
        ranked_nodes = sorted(
            (_normalise_node(node) for node in retrieved),
            key=lambda node: node["similarity"],
            reverse=True,
        )
        relevant_nodes = [
            node for node in ranked_nodes if node["similarity"] >= MIN_SIMILARITY
        ]
        evidence = [
            {
                "feature": node["feature"],
                "decision": node["decision"],
                "content": node["document"],
                "similarity": node["similarity"],
            }
            for node in relevant_nodes
        ]
        message = (
            f"Retrieved {len(retrieved)} node(s); retained "
            f"{len(relevant_nodes)} relevant node(s)."
        )
        logger.info("Context agent: %s", message)
        updates: dict[str, Any] = {
            "retrieved_knowledge_nodes": relevant_nodes,
            "evidence": evidence,
            "processing_logs": [
                build_processing_log("context", "completed", started_at, message)
            ],
        }
        if not relevant_nodes:
            updates["errors"] = [
                "No sufficiently relevant knowledge nodes were found for this question."
            ]
        return updates
    except Exception as exc:
        logger.exception("Context agent retrieval failed")
        message = f"Context retrieval failed: {exc}"
        return {
            "retrieved_knowledge_nodes": [],
            "evidence": [],
            "errors": [message],
            "processing_logs": [
                build_processing_log("context", "failed", started_at, message)
            ],
        }
