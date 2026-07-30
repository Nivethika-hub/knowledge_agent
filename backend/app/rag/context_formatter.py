"""
context_formatter.py

Transforms a list of RetrievedNodes into a single structured context
string that is passed to the LLM prompt.
"""

from typing import List
from app.rag.retriever import RetrievedNode


def format_node(node: RetrievedNode, index: int) -> str:
    """Format one Knowledge Node into a readable text block."""
    participants = ", ".join(node.participants) if node.participants else "Unknown"
    return (
        f"--- Knowledge Node {index} ---\n"
        f"Feature     : {node.feature}\n"
        f"Decision    : {node.decision}\n"
        f"Participants: {participants}\n"
        f"Similarity  : {node.similarity:.2f}\n\n"
        f"{node.document}\n"
        f"{'=' * 60}\n"
    )


def format_context(nodes: List[RetrievedNode]) -> str:
    """
    Merge all retrieved Knowledge Nodes into one structured context block
    that the LLM will use exclusively to generate its answer.
    """
    if not nodes:
        return "No relevant knowledge nodes found."
    blocks = [format_node(n, i + 1) for i, n in enumerate(nodes)]
    return "\n".join(blocks)


def get_avg_similarity(nodes: List[RetrievedNode]) -> float:
    """Compute the mean similarity across retrieved nodes (used for confidence)."""
    if not nodes:
        return 0.0
    return round(sum(n.similarity for n in nodes) / len(nodes), 4)
