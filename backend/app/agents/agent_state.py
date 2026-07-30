"""Shared state and observability models for the Phase 7 agent workflow."""

from __future__ import annotations

from datetime import datetime, timezone
import operator
from typing import Annotated, Any, Literal, TypedDict


AgentName = Literal[
    "coordinator",
    "context",
    "timeline",
    "reasoning",
    "citation",
    "documentation",
]
AgentStatus = Literal["running", "completed", "failed", "skipped"]


class ProcessingLog(TypedDict):
    """A serializable audit entry for one agent execution."""

    agent: AgentName
    status: AgentStatus
    started_at: str
    ended_at: str
    duration_ms: int
    message: str


class AgentState(TypedDict, total=False):
    """State passed between LangGraph nodes.

    All values are JSON-serializable so the completed state can be returned
    directly by FastAPI and inspected in LangGraph tooling.
    """

    question: str
    intent: str
    requested_agents: list[AgentName]
    retrieved_knowledge_nodes: list[dict[str, Any]]
    timeline: list[dict[str, Any]]
    reasoning: dict[str, Any]
    evidence: list[dict[str, Any]]
    citations: list[dict[str, Any]]
    generated_documentation: dict[str, str]
    final_answer: str
    confidence: float
    processing_logs: Annotated[list[ProcessingLog], operator.add]
    errors: Annotated[list[str], operator.add]


def utc_now() -> datetime:
    """Return a timezone-aware timestamp for agent instrumentation."""
    return datetime.now(timezone.utc)


def build_processing_log(
    agent: AgentName,
    status: AgentStatus,
    started_at: datetime,
    message: str,
) -> ProcessingLog:
    """Create a JSON-safe processing log entry after an agent execution."""
    ended_at = utc_now()
    return {
        "agent": agent,
        "status": status,
        "started_at": started_at.isoformat(),
        "ended_at": ended_at.isoformat(),
        "duration_ms": round((ended_at - started_at).total_seconds() * 1000),
        "message": message,
    }


def initial_agent_state(question: str) -> AgentState:
    """Create the complete, safe initial state for an agent run."""
    return {
        "question": question.strip(),
        "intent": "question",
        "requested_agents": [],
        "retrieved_knowledge_nodes": [],
        "timeline": [],
        "reasoning": {},
        "evidence": [],
        "citations": [],
        "generated_documentation": {},
        "final_answer": "",
        "confidence": 0.0,
        "processing_logs": [],
        "errors": [],
    }
