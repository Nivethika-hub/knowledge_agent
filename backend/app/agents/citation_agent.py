"""Citation agent that turns retrieved knowledge-node sources into references."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from app.agents.agent_state import AgentState, build_processing_log, utc_now

logger = logging.getLogger(__name__)

SOURCE_SECTIONS = {
    "Slack Discussions": "Slack",
    "Jira Tickets": "Jira",
    "GitHub Events": "GitHub",
    "Notion Documents": "Notion",
}


def _section_items(document: str, heading: str) -> list[str]:
    """Extract bullet entries from one Phase 5 knowledge-node section."""
    section = document.partition(f"{heading}:\n")[2]
    if not section:
        return []
    next_heading = next(
        (f"\n\n{candidate}:" for candidate in SOURCE_SECTIONS if candidate != heading
         if f"\n\n{candidate}:" in section),
        None,
    )
    if next_heading:
        section = section.partition(next_heading)[0]
    return [line.removeprefix("  - ").strip() for line in section.splitlines()
            if line.strip().startswith("-") and line.removeprefix("  - ").strip()]


def citation_agent(state: AgentState) -> dict[str, Any]:
    """Generate de-duplicated citations without inventing URLs or timestamps."""
    started_at = utc_now()
    timestamps: dict[str, list[str]] = defaultdict(list)
    for event in state.get("timeline", []):
        platform = str(event.get("platform", ""))
        timestamp = str(event.get("timestamp", ""))
        if timestamp and timestamp not in timestamps[platform]:
            timestamps[platform].append(timestamp)

    citations: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for node in state.get("retrieved_knowledge_nodes", []):
        feature = str(node.get("feature", ""))
        document = str(node.get("document", ""))
        for heading, platform in SOURCE_SECTIONS.items():
            for reference in _section_items(document, heading):
                timestamp = ", ".join(timestamps.get(platform, [])) or "Not available"
                key = (platform, reference, feature)
                if key not in seen:
                    seen.add(key)
                    citations.append(
                        {
                            "source": platform,
                            "reference": reference,
                            "timestamp": timestamp,
                            "feature": feature,
                        }
                    )

    message = f"Generated {len(citations)} source citation(s)."
    logger.info("Citation agent: %s", message)
    updates: dict[str, Any] = {
        "citations": citations,
        "processing_logs": [
            build_processing_log("citation", "completed", started_at, message)
        ],
    }
    if not citations:
        updates["errors"] = ["No source references were available for citation."]
    return updates
