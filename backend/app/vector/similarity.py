"""
similarity.py

Higher-level similarity helpers used by the API layer.
Returns top-5 most similar Knowledge Nodes with scores.
"""

from typing import List
from app.vector.retrieval import semantic_search


def get_top_similar(query: str, top_k: int = 5) -> List[dict]:
    """
    Return the top_k most similar Knowledge Nodes for a given query.
    Each result includes: feature, similarity, decision, participants.
    """
    response = semantic_search(query, top_k=top_k)
    return response.get("results", [])


def rank_by_similarity(query: str) -> List[dict]:
    """
    Return ALL stored Knowledge Nodes ranked by similarity to the query.
    Useful for debugging or showing full ranked lists.
    """
    from app.vector.chroma_client import count_documents
    total = count_documents()
    if total == 0:
        return []
    response = semantic_search(query, top_k=total)
    results = response.get("results", [])
    return sorted(results, key=lambda x: x["similarity"], reverse=True)
