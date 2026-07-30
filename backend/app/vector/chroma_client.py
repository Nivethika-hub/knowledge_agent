"""
chroma_client.py

Initialises a persistent ChromaDB client and exposes helper functions
for creating, accessing, and managing the `knowledge_nodes` collection.
The client is created only once (module-level singleton).
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import Optional

_CHROMA_DIR = str(Path(__file__).parents[3] / "data" / "chroma_db")
_COLLECTION_NAME = "knowledge_nodes"

# Singleton persistent client
_client: Optional[chromadb.PersistentClient] = None


def get_chroma_client() -> chromadb.PersistentClient:
    """Return the singleton ChromaDB client, creating it if needed."""
    global _client
    if _client is None:
        Path(_CHROMA_DIR).mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=_CHROMA_DIR)
    return _client


def get_collection() -> chromadb.Collection:
    """Get (or create) the knowledge_nodes collection."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # cosine similarity
    )


def create_collection() -> chromadb.Collection:
    """Force-create a fresh collection (drops existing one)."""
    client = get_chroma_client()
    try:
        client.delete_collection(name=_COLLECTION_NAME)
    except Exception:
        pass
    return client.create_collection(
        name=_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def delete_collection() -> None:
    """Delete the knowledge_nodes collection."""
    client = get_chroma_client()
    client.delete_collection(name=_COLLECTION_NAME)


def count_documents() -> int:
    """Return total number of documents in the collection."""
    return get_collection().count()
