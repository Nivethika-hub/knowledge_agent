"""Knowledge-node regeneration for features changed by the event monitor."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Any

from sqlalchemy.orm import Session

from app.knowledge.ai_service import build_knowledge_node

logger = logging.getLogger(__name__)


def _unique_features(features: Iterable[str | None]) -> list[str]:
    """Normalise feature names while preserving the event-monitor order."""
    unique: list[str] = []
    seen: set[str] = set()
    for feature in features:
        name = str(feature or "").strip()
        key = name.casefold()
        if name and key not in seen:
            seen.add(key)
            unique.append(name)
    return unique


def refresh_knowledge_nodes(
    db: Session, changed_features: Iterable[str | None]
) -> list[dict[str, Any]]:
    """Regenerate every affected Knowledge Node using the existing generator.

    Knowledge Nodes are derived objects rather than database records, so this
    stage intentionally validates generation only.  ``vector_sync`` performs
    the subsequent ChromaDB upsert for each successful feature.
    """
    logger.info("Refreshing Knowledge Nodes...")
    results: list[dict[str, Any]] = []

    for feature_name in _unique_features(changed_features):
        try:
            node = build_knowledge_node(db, feature_name)
            results.append(
                {
                    "feature": feature_name,
                    "knowledge_regenerated": True,
                    "success": True,
                    "timeline_events": len(node.timeline),
                }
            )
        except Exception as exc:
            logger.exception("Knowledge refresh failed for feature %s", feature_name)
            results.append(
                {
                    "feature": feature_name,
                    "knowledge_regenerated": False,
                    "success": False,
                    "error": str(exc),
                }
            )

    return results
