"""
routes/github.py

Endpoints for the `github_events` resource.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db

router = APIRouter(prefix="/github", tags=["GitHub"])


@router.get(
    "",
    response_model=List[schemas.GithubEventResponse],
    summary="List GitHub events",
    description="Returns GitHub events, optionally filtered by project_id.",
)
def list_github_events(
    project_id: Optional[int] = Query(None, description="Filter by project id"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    try:
        return crud.get_github_events(db, project_id=project_id, skip=skip, limit=limit)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch github events: {exc}",
        )
