"""
routes/jira.py

Endpoints for the `jira_tickets` resource.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db

router = APIRouter(prefix="/jira", tags=["Jira"])


@router.get(
    "",
    response_model=List[schemas.JiraTicketResponse],
    summary="List Jira tickets",
    description="Returns Jira tickets, optionally filtered by project_id.",
)
def list_jira_tickets(
    project_id: Optional[int] = Query(None, description="Filter by project id"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    try:
        return crud.get_jira_tickets(db, project_id=project_id, skip=skip, limit=limit)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch jira tickets: {exc}",
        )
