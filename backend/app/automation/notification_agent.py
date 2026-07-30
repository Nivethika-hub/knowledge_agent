"""Create notification records after a successful feature refresh."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Any

from sqlalchemy import MetaData, Table
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

_SUCCESS_MESSAGE = "Knowledge Node regenerated successfully."


def _event_details_by_feature(events: Iterable[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """Keep the first triggering event for each feature."""
    details: dict[str, dict[str, str]] = {}
    for event in events:
        feature = str(event.get("feature") or "").strip()
        if feature and feature.casefold() not in details:
            details[feature.casefold()] = {
                "source": str(event.get("source") or "Automation"),
                "event_type": str(event.get("event_type") or "Knowledge Refresh"),
            }
    return details


def create_refresh_notifications(
    db: Session,
    events: Iterable[dict[str, Any]],
    vector_results: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Insert one unread notification per feature with a successful vector sync.

    The ``notifications`` table was created in Phase 8.1 but has no ORM model
    in this project. Reflection uses that existing schema directly and avoids
    maintaining a duplicate model definition. The caller owns the outer
    transaction and commits after the complete automation workflow succeeds.
    """
    logger.info("Creating Notifications...")
    notifications = Table(
        "notifications", MetaData(), autoload_with=db.get_bind()
    )
    event_details = _event_details_by_feature(events)
    results: list[dict[str, Any]] = []
    notified: set[str] = set()

    for vector_result in vector_results:
        if not vector_result.get("success"):
            continue
        feature = str(vector_result.get("feature") or "").strip()
        feature_key = feature.casefold()
        if not feature or feature_key in notified:
            continue
        notified.add(feature_key)

        trigger = event_details.get(feature_key, {})
        source = trigger.get("source", "Automation")
        try:
            with db.begin_nested():
                result = db.execute(
                    notifications.insert().values(
                        feature_name=feature,
                        event_source=source,
                        event_type="Knowledge Refresh",
                        message=_SUCCESS_MESSAGE,
                        status="Unread",
                    )
                )
            notification_id = result.inserted_primary_key[0]
            results.append(
                {
                    "feature": feature,
                    "notification_created": True,
                    "notification_id": notification_id,
                    "event_source": source,
                    "event_type": "Knowledge Refresh",
                    "success": True,
                }
            )
        except Exception as exc:
            logger.exception("Notification creation failed for feature %s", feature)
            results.append(
                {
                    "feature": feature,
                    "notification_created": False,
                    "success": False,
                    "error": str(exc),
                }
            )

    return results
