"""
routes/projects.py

Endpoints for the `projects` resource.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get(
    "",
    response_model=List[schemas.ProjectResponse],
    summary="List all projects",
    description="Returns every project stored in the system, with optional pagination.",
)
def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    try:
        return crud.get_all_projects(db, skip=skip, limit=limit)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch projects: {exc}",
        )


@router.get(
    "/{project_id}",
    response_model=schemas.ProjectResponse,
    summary="Get a single project",
    description="Returns full details for one project by its project_id.",
)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    return project
