"""Manual Phase 8 automation endpoint.

Automation is deliberately request-driven: no background scheduler or worker
process invokes this workflow.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.automation.event_monitor import detect_new_events
from app.automation.knowledge_refresh import refresh_knowledge_nodes
from app.automation.notification_agent import create_refresh_notifications
from app.automation.vector_sync import sync_feature_vectors
from app.dependencies import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/automation", tags=["Automation"])


def _successful_features(results: list[dict[str, Any]]) -> list[str]:
    """Extract the features allowed to progress to the next automation step."""
    return [str(result["feature"]) for result in results if result.get("success")]


def _failed_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return only failed stage results for a safe API error payload."""
    return [result for result in results if not result.get("success")]


@router.post("/run", summary="Run manual knowledge automation")
def run_automation(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Detect events and refresh only their affected Knowledge Nodes.

    This endpoint is the sole automation trigger. It performs no scheduling,
    polling, or background work outside this request.
    """
    try:
        events = detect_new_events(db)
    except SQLAlchemyError as exc:
        logger.exception("Automation event monitoring failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unavailable while checking events: {exc}",
        ) from exc
    except Exception as exc:
        logger.exception("Automation event monitoring failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Event monitoring failed: {exc}",
        ) from exc

    if not events:
        logger.info("Automation Complete. No new events detected.")
        return {
            "events_detected": 0,
            "updated_features": [],
            "vectors_updated": 0,
            "notifications_created": 0,
            "status": "Automation completed successfully",
        }

    changed_features = [event["feature"] for event in events if event.get("feature")]
    try:
        refresh_results = refresh_knowledge_nodes(db, changed_features)
    except Exception as exc:
        db.rollback()
        logger.exception("Automation knowledge refresh failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Knowledge generation failure: {exc}",
        ) from exc
    failures = _failed_results(refresh_results)
    if failures:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"stage": "knowledge_refresh", "failures": failures},
        )

    try:
        vector_results = sync_feature_vectors(db, _successful_features(refresh_results))
    except Exception as exc:
        db.rollback()
        logger.exception("Automation vector sync failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Embedding failure: {exc}",
        ) from exc
    failures = _failed_results(vector_results)
    if failures:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"stage": "vector_sync", "failures": failures},
        )

    try:
        notification_results = create_refresh_notifications(db, events, vector_results)
    except Exception as exc:
        db.rollback()
        logger.exception("Automation notification creation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Notification insertion failure: {exc}",
        ) from exc
    failures = _failed_results(notification_results)
    if failures:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"stage": "notification_agent", "failures": failures},
        )

    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Automation notification commit failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Notification insertion failure: {exc}",
        ) from exc

    updated_features = _successful_features(vector_results)
    logger.info("Automation Complete.")
    return {
        "events_detected": len(events),
        "updated_features": updated_features,
        "vectors_updated": len(updated_features),
        "notifications_created": sum(
            1 for result in notification_results if result.get("notification_created")
        ),
        "status": "Automation completed successfully",
    }
