"""
retriever.py

Retrieves the top-k most semantically similar Knowledge Nodes from
ChromaDB for a given natural language question.
Wraps Phase 5 vector retrieval and enriches results with metadata.
"""

from typing import List
from app.vector.retrieval import semantic_search


class RetrievedNode:
    """Holds a single retrieved Knowledge Node with its similarity score."""

    def __init__(self, feature: str, similarity: float, decision: str,
                 participants: List[str], document: str):
        self.feature = feature
        self.similarity = similarity
        self.decision = decision
        self.participants = participants
        self.document = document

    def to_dict(self) -> dict:
        return {
            "feature": self.feature,
            "similarity": self.similarity,
            "decision": self.decision,
            "participants": self.participants,
            "document": self.document,
        }


def retrieve(question: str, top_k: int = 5) -> List[RetrievedNode]:
    """
    Embed the question and retrieve the top_k most similar Knowledge Nodes.
    Returns an empty list when the collection is empty or no results match.
    """
    raw = semantic_search(question, top_k=top_k)
    nodes = []
    for r in raw.get("results", []):
        nodes.append(RetrievedNode(
            feature=r.get("feature", ""),
            similarity=r.get("similarity", 0.0),
            decision=r.get("decision", ""),
            participants=r.get("participants", []),
            document=r.get("document", ""),
        ))
    return nodes


def retrieve_dicts(question: str, top_k: int = 5) -> List[dict]:
    """Convenience wrapper — returns plain dicts instead of objects."""
    return [n.to_dict() for n in retrieve(question, top_k=top_k)]
