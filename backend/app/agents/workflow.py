"""LangGraph orchestration for the autonomous knowledge-agent system."""

from __future__ import annotations

import logging
from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.agents.agent_state import AgentState, initial_agent_state
from app.agents.citation_agent import citation_agent
from app.agents.context_agent import context_agent
from app.agents.coordinator_agent import coordinator_agent
from app.agents.documentation_agent import documentation_agent
from app.agents.reasoning_agent import reasoning_agent
from app.agents.timeline_agent import timeline_agent

logger = logging.getLogger(__name__)

WORKFLOW_STEPS = [
    "Coordinator",
    "Context Agent",
    "Timeline Agent",
    "Reasoning Agent",
    "Citation Agent",
    "Documentation Agent (when requested)",
    "Coordinator",
]


def _documentation_route(
    state: AgentState,
) -> Literal["documentation", "finalize"]:
    """Select the optional documentation branch from the coordinator plan."""
    if "documentation" in state.get("requested_agents", []):
        return "documentation"
    return "finalize"


def build_agent_workflow():
    """Compile the reusable Phase 7 LangGraph workflow exactly once per import."""
    graph = StateGraph(AgentState)
    graph.add_node("coordinate", coordinator_agent)
    graph.add_node("context", context_agent)
    graph.add_node("timeline", timeline_agent)
    graph.add_node("reasoning", reasoning_agent)
    graph.add_node("citation", citation_agent)
    graph.add_node("documentation", documentation_agent)
    graph.add_node("finalize", coordinator_agent)

    graph.add_edge(START, "coordinate")
    graph.add_edge("coordinate", "context")
    graph.add_edge("context", "timeline")
    graph.add_edge("timeline", "reasoning")
    graph.add_edge("reasoning", "citation")
    graph.add_conditional_edges(
        "citation",
        _documentation_route,
        {"documentation": "documentation", "finalize": "finalize"},
    )
    graph.add_edge("documentation", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile()


agent_workflow = build_agent_workflow()


def run_agent_workflow(question: str) -> AgentState:
    """Run the complete graph and return its JSON-serializable final state."""
    logger.info("Starting agent workflow for question: %s", question)
    return agent_workflow.invoke(initial_agent_state(question))


def workflow_visualization() -> dict[str, list[str]]:
    """Return a display-friendly description of the executable workflow."""
    return {"steps": WORKFLOW_STEPS}
