"""
answer_generator.py

Orchestrates a single RAG inference cycle:
  1. Retrieve relevant Knowledge Nodes
  2. Format them into LLM context
  3. Build the prompt
  4. Call the Groq LLM
  5. Assemble citations
  6. Return a structured answer dict

This module is designed to be reusable and swappable — Phase 7 agents
can call generate_answer() directly without touching retrieval or storage.
"""

from typing import List
from datetime import datetime

from app.rag.retriever import retrieve, RetrievedNode
from app.rag.context_formatter import format_context, get_avg_similarity
from app.rag.prompt_builder import build_prompt, SYSTEM_PROMPT
from app.rag.llm_service import call_llm_with_system
from app.rag.citation_builder import build_citations


_NO_EVIDENCE_REPLY = (
    "I couldn't find evidence for that in the available organisational knowledge."
)


def _build_user_message(question: str, context: str) -> str:
    return (
        f"=== KNOWLEDGE CONTEXT ===\n{context}\n\n"
        f"=== USER QUESTION ===\n{question}\n\n"
        "Based only on the Knowledge Context above, provide a structured answer "
        "with Summary, Reasoning, Evidence, and Participants."
    )


def generate_answer(question: str, top_k: int = 5) -> dict:
    """
    Full RAG pipeline: retrieve → format → prompt → LLM → structure.

    Returns a dict matching the Phase 6 answer schema.
    """
    if not question.strip():
        return {
            "question": question,
            "answer": "Question cannot be empty.",
            "confidence": 0.0,
            "sources": [],
            "timeline": [],
            "retrieved_nodes": 0,
            "generated_at": datetime.utcnow().isoformat(),
        }

    # 1. Retrieve
    nodes: List[RetrievedNode] = retrieve(question, top_k=top_k)

    if not nodes:
        return {
            "question": question,
            "answer": _NO_EVIDENCE_REPLY,
            "confidence": 0.0,
            "sources": [],
            "timeline": [],
            "retrieved_nodes": 0,
            "generated_at": datetime.utcnow().isoformat(),
        }

    # 2. Format context
    context = format_context(nodes)
    confidence = get_avg_similarity(nodes)

    # 3. Call LLM
    user_message = _build_user_message(question, context)
    try:
        llm_answer = call_llm_with_system(
            system=SYSTEM_PROMPT,
            user_message=user_message,
            temperature=0.1,
            max_tokens=1024,
        )
    except Exception as exc:
        return {
            "question": question,
            "answer": f"LLM call failed: {exc}",
            "confidence": confidence,
            "sources": [],
            "timeline": [],
            "retrieved_nodes": len(nodes),
            "generated_at": datetime.utcnow().isoformat(),
        }

    # 4. Build citations
    sources = build_citations(nodes)

    # 5. Build timeline from retrieved nodes (top features)
    timeline = [
        {"feature": n.feature, "similarity": n.similarity}
        for n in nodes
    ]

    return {
        "question": question,
        "answer": llm_answer,
        "confidence": confidence,
        "sources": sources,
        "timeline": timeline,
        "retrieved_nodes": len(nodes),
        "generated_at": datetime.utcnow().isoformat(),
    }


def generate_debug_info(question: str, top_k: int = 5) -> dict:
    """
    Returns a complete debug payload: retrieved nodes, context,
    the exact prompt sent to the LLM, and the raw LLM response.
    """
    nodes = retrieve(question, top_k=top_k)
    context = format_context(nodes)
    user_message = _build_user_message(question, context)
    full_prompt = f"[SYSTEM]\n{SYSTEM_PROMPT}\n\n[USER]\n{user_message}"

    raw_response = ""
    error = None
    try:
        raw_response = call_llm_with_system(
            system=SYSTEM_PROMPT,
            user_message=user_message,
            temperature=0.1,
            max_tokens=1024,
        )
    except Exception as exc:
        error = str(exc)

    return {
        "question": question,
        "retrieved_nodes": [n.to_dict() for n in nodes],
        "formatted_context": context,
        "prompt_sent_to_llm": full_prompt,
        "raw_llm_response": raw_response,
        "error": error,
    }
