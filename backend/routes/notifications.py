"""Read-only notification feed for automation results."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import MetaData, Table, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.dependencies import get_db

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", summary="List knowledge refresh notifications")
def list_notifications(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """Return the newest automation notifications first."""
    try:
        notifications = Table("notifications", MetaData(), autoload_with=db.get_bind())
        rows = db.execute(select(notifications).order_by(notifications.c.created_at.desc())).mappings().all()
        return [dict(row) for row in rows]
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Notifications are unavailable: {exc}") from exc
