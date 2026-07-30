"""In-memory monitoring for newly inserted enterprise-source records.

The monitor intentionally persists no state in PostgreSQL.  Its first call
captures the current high-water marks; later calls return records added after
those marks while the FastAPI process remains alive.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Any

from sqlalchemy.orm import Session

from app.models import GithubEvent, JiraTicket, NotionDocument, SlackMessage

logger = logging.getLogger(__name__)

# A value of None means that source has not yet been baselined in this process.
last_processed_ids: dict[str, int | None] = {
    "slack": None,
    "jira": None,
    "github": None,
    "notion": None,
}

_SOURCES = (
    ("slack", "Slack", SlackMessage, "message_id"),
    ("jira", "Jira", JiraTicket, "jira_id"),
    ("github", "GitHub", GithubEvent, "github_event_id"),
    ("notion", "Notion", NotionDocument, "document_id"),
)


def _event_type(source_key: str, row: Any) -> str:
    """Return a readable event type without inventing source data."""
    if source_key == "github" and row.event_type:
        return str(row.event_type)
    return {
        "slack": "Slack message",
        "jira": "Jira ticket",
        "github": "GitHub event",
        "notion": "Notion document",
    }[source_key]


def _serialise_events(
    source_key: str,
    source_name: str,
    id_column: str,
    rows: Iterable[Any],
) -> list[dict[str, Any]]:
    """Convert source rows into the route-friendly event contract."""
    return [
        {
            "feature": row.related_feature,
            "source": source_name,
            "event_id": getattr(row, id_column),
            "event_type": _event_type(source_key, row),
        }
        for row in rows
        if row.related_feature
    ]


def detect_new_events(db: Session) -> list[dict[str, Any]]:
    """Return source rows inserted since the previous monitor invocation.

    The first invocation creates an in-memory high-water-mark baseline and
    returns no events.  This prevents an automation service restart from
    reprocessing the full historical dataset.
    """
    detected: list[dict[str, Any]] = []

    for source_key, source_name, model, id_column in _SOURCES:
        logger.info("Checking %s...", source_name)
        primary_key = getattr(model, id_column)
        current_max = db.query(primary_key).order_by(primary_key.desc()).limit(1).scalar()
        previous_max = last_processed_ids[source_key]

        if previous_max is None:
            last_processed_ids[source_key] = current_max or 0
            continue

        if current_max is None or current_max <= previous_max:
            continue

        rows = (
            db.query(model)
            .filter(primary_key > previous_max)
            .order_by(primary_key.asc())
            .all()
        )
        detected.extend(_serialise_events(source_key, source_name, id_column, rows))
        last_processed_ids[source_key] = current_max

    logger.info("Detected %s event(s).", len(detected))
    return detected
