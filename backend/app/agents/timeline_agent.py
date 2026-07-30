"""Agent that reconstructs a chronological timeline from retrieved evidence."""

from __future__ import annotations

import logging
import re
from typing import Any

from app.agents.agent_state import AgentState, build_processing_log, utc_now

logger = logging.getLogger(__name__)

TIMELINE_LINE = re.compile(
    r"^\s*(?P<time>\d{1,2}:\d{2})\s+\[(?P<platform>[^\]]+)\]\s*"
    r"(?P<title>.+?)\s*$",
    re.MULTILINE,
)


def _events_from_node(node: dict[str, Any]) -> list[dict[str, str]]:
    """Parse the stable Timeline section produced by Phase 5 ingestion."""
    document = str(node.get("document", ""))
    timeline_section = document.partition("Timeline:\n")[2].partition(
        "\n\nSlack Discussions:"
    )[0]
    events = []
    for match in TIMELINE_LINE.finditer(timeline_section):
        events.append(
            {
                "timestamp": match.group("time"),
                "platform": match.group("platform"),
                "title": match.group("title"),
                "feature": str(node.get("feature", "")),
            }
        )
    return events


def timeline_agent(state: AgentState) -> dict[str, Any]:
    """Build a source-preserving, chronological timeline from retrieved nodes."""
    started_at = utc_now()
    try:
        events = [
            event
            for node in state.get("retrieved_knowledge_nodes", [])
            for event in _events_from_node(node)
        ]
        unique_events = {
            (event["timestamp"], event["platform"], event["title"], event["feature"]): event
            for event in events
        }
        timeline = sorted(
            unique_events.values(),
            key=lambda event: (event["timestamp"], event["platform"], event["title"]),
        )
        message = f"Built a timeline with {len(timeline)} event(s)."
        logger.info("Timeline agent: %s", message)
        updates: dict[str, Any] = {
            "timeline": timeline,
            "processing_logs": [
                build_processing_log("timeline", "completed", started_at, message)
            ],
        }
        if not timeline:
            updates["errors"] = [
                "No timestamped events were present in the retrieved knowledge nodes."
            ]
        return updates
    except Exception as exc:
        logger.exception("Timeline reconstruction failed")
        message = f"Timeline reconstruction failed: {exc}"
        return {
            "timeline": [],
            "errors": [message],
            "processing_logs": [
                build_processing_log("timeline", "failed", started_at, message)
            ],
        }
