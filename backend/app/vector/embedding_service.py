"""
Loads the sentence-transformer model ONCE and exposes functions to
generate embeddings for text strings and document batches.
Model: sentence-transformers/all-MiniLM-L6-v2
"""

from pathlib import Path
from typing import List
import re

from huggingface_hub import scan_cache_dir
from sentence_transformers import SentenceTransformer

_MODEL: SentenceTransformer | None = None
_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def _cached_model_path() -> str | None:
    """Return a complete cached model snapshot, when one is available.

    Hugging Face caches may contain an incomplete active revision after an
    interrupted download. Selecting a snapshot that contains model weights
    keeps embedding loading deterministic while still allowing a normal remote
    download when no complete local snapshot exists.
    """
    try:
        cache = scan_cache_dir()
    except OSError:
        return None

    for repository in cache.repos:
        if repository.repo_id != _MODEL_NAME:
            continue
        revisions = sorted(
            repository.revisions,
            key=lambda revision: revision.last_modified,
            reverse=True,
        )
        for revision in revisions:
            snapshot = Path(revision.snapshot_path)
            if (snapshot / "model.safetensors").is_file():
                return str(snapshot)
    return None


def load_embedding_model() -> SentenceTransformer:
    """Singleton loader - loads the model only once, reuses it on every call."""
    global _MODEL
    if _MODEL is None:
        cached_path = _cached_model_path()
        _MODEL = SentenceTransformer(
            cached_path or _MODEL_NAME,
            local_files_only=cached_path is not None,
        )
    return _MODEL


def normalize_text(text: str) -> str:
    """Strip excess whitespace and lower-case to improve embedding quality."""
    text = re.sub(r"\s+", " ", text).strip()
    return text


def embed_text(text: str) -> List[float]:
    """Embed a single string and return a flat list of floats."""
    model = load_embedding_model()
    text = normalize_text(text)
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def embed_documents(documents: List[str]) -> List[List[float]]:
    """Batch-embed a list of documents. More efficient than calling embed_text in a loop."""
    model = load_embedding_model()
    normalized = [normalize_text(d) for d in documents]
    embeddings = model.encode(normalized, convert_to_numpy=True, batch_size=32)
    return [e.tolist() for e in embeddings]