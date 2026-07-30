"""
routes/slack.py

Endpoints for the `slack_messages` resource.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db

router = APIRouter(prefix="/slack", tags=["Slack"])


@router.get(
    "",
    response_model=List[schemas.SlackMessageResponse],
    summary="List Slack messages",
    description="Returns Slack messages, optionally filtered by project_id.",
)
def list_slack_messages(
    project_id: Optional[int] = Query(None, description="Filter by project id"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    try:
        return crud.get_slack_messages(db, project_id=project_id, skip=skip, limit=limit)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch slack messages: {exc}",
        )
