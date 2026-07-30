"""
routes/notion.py

Endpoints for the `notion_documents` resource.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db

router = APIRouter(prefix="/notion", tags=["Notion"])


@router.get(
    "",
    response_model=List[schemas.NotionDocumentResponse],
    summary="List Notion documents",
    description="Returns Notion documents, optionally filtered by project_id.",
)
def list_notion_documents(
    project_id: Optional[int] = Query(None, description="Filter by project id"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    try:
        return crud.get_notion_documents(db, project_id=project_id, skip=skip, limit=limit)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notion documents: {exc}",
        )
