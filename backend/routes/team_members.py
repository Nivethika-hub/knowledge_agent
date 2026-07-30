"""
routes/team_members.py

Endpoints for the `team_members` resource.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db

router = APIRouter(prefix="/team-members", tags=["Team Members"])


@router.get(
    "",
    response_model=List[schemas.TeamMemberResponse],
    summary="List team members",
    description="Returns team members, optionally filtered by project_id.",
)
def list_team_members(
    project_id: Optional[int] = Query(None, description="Filter by project id"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    try:
        return crud.get_team_members(db, project_id=project_id, skip=skip, limit=limit)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch team members: {exc}",
        )


@router.get(
    "/{member_id}",
    response_model=schemas.TeamMemberResponse,
    summary="Get a single team member",
    description="Returns full details for one team member by member_id.",
)
def get_team_member(member_id: int, db: Session = Depends(get_db)):
    member = crud.get_team_member_by_id(db, member_id)
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team member with id {member_id} not found",
        )
    return member
