"""
rag_pipeline.py

Public facade for the RAG pipeline.
Phase 7 agents should import from here rather than individual modules,
keeping the internal chain flexible and replaceable.
"""

from app.rag.answer_generator import generate_answer, generate_debug_info
from app.rag.retriever import retrieve_dicts

__all__ = ["run_pipeline", "run_debug_pipeline", "retrieve_context"]


def run_pipeline(question: str, top_k: int = 5) -> dict:
    """
    Main entry point for the RAG pipeline.
    Accepts a raw user question and returns the structured answer dict.
    """
    return generate_answer(question, top_k=top_k)


def run_debug_pipeline(question: str, top_k: int = 5) -> dict:
    """
    Debug entry point — returns the full pipeline trace including
    retrieved nodes, prompt, and raw LLM response.
    """
    return generate_debug_info(question, top_k=top_k)


def retrieve_context(question: str, top_k: int = 5) -> list[dict]:
    """
    Retrieval-only entry point.
    Useful for agents that handle LLM calls themselves (Phase 7).
    """
    return retrieve_dicts(question, top_k=top_k)
