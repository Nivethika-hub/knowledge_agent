"""
routes/knowledge.py

The Phase 4 endpoints that generate structured Knowledge Nodes
using deterministic heuristic logic.

    GET /knowledge/{feature_name} -> Return one KnowledgeNode
    GET /knowledge                -> Return all generated Knowledge Nodes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.knowledge.knowledge_models import KnowledgeNode
from app.knowledge.ai_service import build_knowledge_node, get_all_features

router = APIRouter(prefix="/knowledge", tags=["Knowledge Generation"])

@router.get(
    "/{feature_name}",
    response_model=KnowledgeNode,
    summary="Generate Knowledge Node for a feature",
    description="Transforms raw platform data into a structured Knowledge Node using deterministic heuristics.",
)
def get_knowledge_node(feature_name: str, db: Session = Depends(get_db)):
    try:
        node = build_knowledge_node(db, feature_name)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
        
    if not node.timeline and not node.slack_messages and not node.jira_tickets and not node.notion_documents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No records found for feature '{feature_name}'"
        )
        
    return node


@router.get(
    "",
    response_model=List[KnowledgeNode],
    summary="Generate all Knowledge Nodes",
    description="Iterates over all features in the database and generates a Knowledge Node for each.",
)
def get_all_knowledge_nodes(db: Session = Depends(get_db)):
    features = get_all_features(db)
    
    nodes = []
    for f in features:
        if f: # Skip empty/None features
            nodes.append(build_knowledge_node(db, f))
            
    return nodes

