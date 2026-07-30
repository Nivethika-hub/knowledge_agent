"""
routes/vector.py

Phase 5 FastAPI routes for vector semantic search.

    GET  /vector/search?q=...   → Semantic search over Knowledge Nodes
    POST /vector/reindex        → Rebuild entire ChromaDB index from DB
    GET  /vector/count          → Total number of indexed documents
    GET  /vector/features       → List all indexed feature names
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.vector.retrieval import semantic_search, search_by_similarity
from app.vector.ingestion import ingest_all_knowledge_nodes, ingest_feature
from app.vector.chroma_client import count_documents, get_collection

router = APIRouter(prefix="/vector", tags=["Semantic Search"])


@router.get(
    "/search",
    summary="Semantic search over Knowledge Nodes",
    description=(
        "Embed the query and return the most similar Knowledge Nodes "
        "from ChromaDB. Use `top_k` to control how many results to return."
    ),
)
def vector_search(
    q: str = Query(..., description="Natural language search query"),
    top_k: int = Query(5, ge=1, le=20, description="Max number of results"),
    threshold: float = Query(0.0, ge=0.0, le=1.0, description="Minimum similarity score"),
    db: Session = Depends(get_db),
):
    if not q.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter 'q' cannot be empty.",
        )
    if threshold > 0.0:
        return search_by_similarity(q, threshold=threshold)
    return semantic_search(q, top_k=top_k)


@router.post(
    "/reindex",
    summary="Reindex all Knowledge Nodes into ChromaDB",
    description=(
        "Regenerate the ChromaDB index by loading every unique feature "
        "from PostgreSQL, building its Knowledge Node, and upserting "
        "the embedding. Safe to call multiple times."
    ),
)
def reindex(db: Session = Depends(get_db)):
    try:
        result = ingest_all_knowledge_nodes(db)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reindex failed: {exc}",
        )
    return result


@router.post(
    "/reindex/{feature_name}",
    summary="Reindex a single Knowledge Node",
    description="Index (or refresh) a single feature's Knowledge Node in ChromaDB.",
)
def reindex_feature(feature_name: str, db: Session = Depends(get_db)):
    try:
        result = ingest_feature(db, feature_name)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index feature '{feature_name}': {exc}",
        )
    return result


@router.get(
    "/count",
    summary="Total indexed document count",
)
def get_count():
    return {"total_indexed": count_documents()}


@router.get(
    "/features",
    summary="List all indexed feature names",
    response_model=List[str],
)
def list_features():
    collection = get_collection()
    raw = collection.get(include=["metadatas"])
    features = [m.get("feature_name", "") for m in raw.get("metadatas", [])]
    return [f for f in features if f]
