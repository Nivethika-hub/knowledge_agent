"""
retrieval.py

Semantic retrieval functions that query ChromaDB using embedding
similarity. Returns structured results ready to be used as LLM context
in Phase 6.
"""

from typing import List
from app.vector.chroma_client import get_collection
from app.vector.embedding_service import embed_text
import json


def _parse_participants(raw: str) -> List[str]:
    """Parse participants — stored as JSON string in Chroma metadata."""
    try:
        return json.loads(raw) if raw else []
    except Exception:
        return [raw]


def _format_results(chroma_results: dict, query: str) -> dict:
    """Convert raw Chroma response into the standard search response format."""
    results = []
    ids = chroma_results.get("ids", [[]])[0]
    docs = chroma_results.get("documents", [[]])[0]
    metas = chroma_results.get("metadatas", [[]])[0]
    distances = chroma_results.get("distances", [[]])[0]

    for doc_id, doc, meta, dist in zip(ids, docs, metas, distances):
        # ChromaDB cosine distance → similarity score (1 - distance)
        similarity = round(1 - dist, 4)
        participants = _parse_participants(meta.get("participants", "[]"))
        results.append({
            "feature": meta.get("feature_name", doc_id),
            "similarity": similarity,
            "decision": meta.get("decision", ""),
            "participants": participants,
            "document": doc,
        })

    return {"query": query, "results": results}


def semantic_search(query: str, top_k: int = 5) -> dict:
    """Embed the query and return the top_k most similar Knowledge Nodes."""
    collection = get_collection()
    if collection.count() == 0:
        return {"query": query, "results": [], "error": "Collection is empty. Run /vector/reindex first."}

    query_embedding = embed_text(query)
    raw = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )
    return _format_results(raw, query)


def top_k_search(query: str, k: int = 5) -> dict:
    """Alias for semantic_search with explicit k parameter."""
    return semantic_search(query, top_k=k)


def feature_search(feature_name: str) -> dict:
    """Retrieve a specific Knowledge Node by exact feature name."""
    collection = get_collection()
    doc_id = feature_name.strip().lower().replace(" ", "_")
    raw = collection.get(ids=[doc_id], include=["documents", "metadatas"])

    if not raw["ids"]:
        return {"query": feature_name, "results": [], "error": f"Feature '{feature_name}' not found in vector store."}

    results = []
    for fid, doc, meta in zip(raw["ids"], raw["documents"], raw["metadatas"]):
        participants = _parse_participants(meta.get("participants", "[]"))
        results.append({
            "feature": meta.get("feature_name", fid),
            "similarity": 1.0,
            "decision": meta.get("decision", ""),
            "participants": participants,
            "document": doc,
        })
    return {"query": feature_name, "results": results}


def search_by_similarity(query: str, threshold: float = 0.5) -> dict:
    """Return only results with similarity above the given threshold."""
    raw = semantic_search(query, top_k=10)
    raw["results"] = [r for r in raw["results"] if r["similarity"] >= threshold]
    return raw
