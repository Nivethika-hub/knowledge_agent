"""Targeted ChromaDB updates for refreshed Knowledge Nodes."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Any

from sqlalchemy.orm import Session

from app.vector.ingestion import ingest_feature

logger = logging.getLogger(__name__)


def _unique_features(features: Iterable[str | None]) -> list[str]:
    """Remove blank and duplicate feature names without changing their order."""
    unique: list[str] = []
    seen: set[str] = set()
    for feature in features:
        name = str(feature or "").strip()
        key = name.casefold()
        if name and key not in seen:
            seen.add(key)
            unique.append(name)
    return unique


def sync_feature_vectors(
    db: Session, changed_features: Iterable[str | None]
) -> list[dict[str, Any]]:
    """Regenerate and upsert embeddings for only the supplied features.

    ``ingest_feature`` is the existing Phase 5 ingestion path: it rebuilds the
    derived Knowledge Node, embeds it, and upserts the stable document ID into
    the existing ``knowledge_nodes`` collection.
    """
    logger.info("Updating ChromaDB...")
    results: list[dict[str, Any]] = []

    for feature_name in _unique_features(changed_features):
        try:
            ingestion = ingest_feature(db, feature_name)
            results.append(
                {
                    "feature": feature_name,
                    "vector_updated": ingestion.get("status") == "indexed",
                    "embedding_regenerated": ingestion.get("status") == "indexed",
                    "document_id": ingestion.get("doc_id"),
                    "success": ingestion.get("status") == "indexed",
                }
            )
        except Exception as exc:
            logger.exception("Vector sync failed for feature %s", feature_name)
            results.append(
                {
                    "feature": feature_name,
                    "vector_updated": False,
                    "embedding_regenerated": False,
                    "success": False,
                    "error": str(exc),
                }
            )

    return results
