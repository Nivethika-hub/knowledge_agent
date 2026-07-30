"""
vector_store.py

CRUD operations for Knowledge Nodes inside ChromaDB.
Keeps embedding and storage logic fully separated.
"""

from typing import Optional
from app.vector.chroma_client import get_collection
from app.vector.embedding_service import embed_text
import json


def _build_id(feature_name: str) -> str:
    """Generate a stable document ID from the feature name."""
    return feature_name.strip().lower().replace(" ", "_")


def insert_node(doc_id: str, text: str, metadata: dict) -> None:
    """Insert a single Knowledge Node document into ChromaDB."""
    collection = get_collection()
    embedding = embed_text(text)
    # Ensure all metadata values are JSON-serialisable primitives
    safe_meta = {k: (json.dumps(v) if isinstance(v, (list, dict)) else v)
                 for k, v in metadata.items()}
    collection.upsert(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[safe_meta],
    )


def insert_nodes(nodes: list[dict]) -> None:
    """
    Batch insert a list of node dicts.
    Each dict must contain: id, text, metadata.
    """
    from app.vector.embedding_service import embed_documents

    collection = get_collection()
    ids = [n["id"] for n in nodes]
    texts = [n["text"] for n in nodes]
    embeddings = embed_documents(texts)
    metadatas = []
    for n in nodes:
        safe = {k: (json.dumps(v) if isinstance(v, (list, dict)) else v)
                for k, v in n["metadata"].items()}
        metadatas.append(safe)

    collection.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)


def update_node(doc_id: str, text: str, metadata: dict) -> None:
    """Update an existing node (upsert semantics)."""
    insert_node(doc_id, text, metadata)


def delete_node(doc_id: str) -> None:
    """Delete a node by its ID."""
    collection = get_collection()
    collection.delete(ids=[doc_id])


def list_nodes(limit: int = 100) -> list[dict]:
    """Return up to `limit` stored documents with their metadata."""
    collection = get_collection()
    results = collection.get(limit=limit, include=["documents", "metadatas"])
    output = []
    for doc_id, doc, meta in zip(results["ids"], results["documents"], results["metadatas"]):
        output.append({"id": doc_id, "document": doc, "metadata": meta})
    return output
