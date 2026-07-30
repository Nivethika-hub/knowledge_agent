"""
routes/ask.py

Phase 6 RAG endpoints.

    POST /ask              → Answer a natural language question via RAG
    GET  /ask/sample       → Try a sample question (no body needed)
    GET  /ask/history      → Placeholder for conversation history (Phase 7)
    POST /ask/debug        → Full pipeline trace for development
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.rag.rag_pipeline import run_pipeline, run_debug_pipeline

router = APIRouter(prefix="/ask", tags=["RAG — Question Answering"])

# In-memory answer history (Phase 7 will persist this to the DB)
_history: list[dict] = []

SAMPLE_QUESTIONS = [
    "Why did the team choose PostgreSQL?",
    "Who worked on the JWT Authentication feature?",
    "What was the timeline for the Database Design decision?",
    "Which Jira tickets are related to the Dashboard feature?",
    "What did the team decide about the notification system?",
]


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 5


# ── POST /ask ─────────────────────────────────────────────────────────────────

@router.post(
    "",
    summary="Ask the Knowledge Agent a question",
    description=(
        "Runs the full RAG pipeline: semantic retrieval from ChromaDB → "
        "Groq LLM answer generation → structured JSON response with citations."
    ),
)
def ask_question(body: QuestionRequest):
    if not body.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )

    try:
        result = run_pipeline(body.question, top_k=body.top_k)
    except RuntimeError as exc:
        # Raised when GROQ_API_KEY is missing
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG pipeline error: {exc}",
        )

    # Store in session history
    _history.append({"question": body.question, "answer": result.get("answer", "")})
    if len(_history) > 50:
        _history.pop(0)

    return result


# ── GET /ask/sample ───────────────────────────────────────────────────────────

@router.get(
    "/sample",
    summary="Run a sample question through the RAG pipeline",
    description="Runs a preset sample question. Useful to verify the pipeline is working.",
)
def ask_sample():
    question = SAMPLE_QUESTIONS[0]
    try:
        return run_pipeline(question, top_k=5)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


# ── GET /ask/history ──────────────────────────────────────────────────────────

@router.get(
    "/history",
    summary="Get recent question-answer history",
    description="Returns the last 50 questions asked in this session.",
)
def get_history():
    return {
        "total": len(_history),
        "history": list(reversed(_history)),  # newest first
    }


# ── POST /ask/debug ───────────────────────────────────────────────────────────

@router.post(
    "/debug",
    summary="Debug the RAG pipeline",
    description=(
        "Returns the full pipeline trace: retrieved Knowledge Nodes, "
        "formatted context, the exact prompt sent to the LLM, and the raw response."
    ),
)
def ask_debug(body: QuestionRequest):
    if not body.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )
    try:
        return run_debug_pipeline(body.question, top_k=body.top_k)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
