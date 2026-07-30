"""
ai_service.py

Exposes simple wrappers over the knowledge generators.
Currently deterministic, will be updated to use LLM calls in Phase 5.
"""

from sqlalchemy.orm import Session
from app.knowledge.knowledge_generator import generate_knowledge_node
from app.knowledge.knowledge_models import KnowledgeNode
from app.models import SlackMessage

def build_knowledge_node(db: Session, feature_name: str) -> KnowledgeNode:
    return generate_knowledge_node(db, feature_name)

def search_decision(db: Session, feature_name: str) -> str:
    node = generate_knowledge_node(db, feature_name)
    return node.decision

def answer_feature_question(db: Session, feature_name: str) -> str:
    """
    Simulates answering a feature question.
    In Phase 5, this will pass the node to an LLM.
    """
    node = generate_knowledge_node(db, feature_name)
    return f"Feature: {node.feature_name}\nDecision: {node.decision}\nReasoning: {node.reason}"

def get_all_features(db: Session) -> list[str]:
    """
    Utility to get all unique feature names from the database.
    We grab from SlackMessage for simplicity, but in a real DB it could check all tables.
    """
    features = db.query(SlackMessage.related_feature).filter(SlackMessage.related_feature != None).distinct().all()
    return [f[0] for f in features]

