"""Phase 7 endpoints for the LangGraph multi-agent knowledge system."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from app.agents.workflow import run_agent_workflow, workflow_visualization

router = APIRouter(prefix="/agent", tags=["Autonomous Multi-Agent System"])

WORKFLOW_TIMEOUT_SECONDS = 45
SAMPLE_QUESTION = "Why did the team choose PostgreSQL?"


class AgentQuestionRequest(BaseModel):
    """Request model for evidence-based questions."""

    question: str = Field(min_length=1, max_length=2_000)


class AgentDocumentRequest(BaseModel):
    """Request model for documentation generation."""

    feature: str = Field(min_length=1, max_length=500)


async def _run_workflow(question: str) -> dict[str, Any]:
    """Execute the synchronous LangGraph workflow with an API timeout."""
    try:
        return await asyncio.wait_for(
            run_in_threadpool(run_agent_workflow, question),
            timeout=WORKFLOW_TIMEOUT_SECONDS,
        )
    except TimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The agent workflow exceeded the 45-second timeout.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent workflow failed: {exc}",
        ) from exc


@router.post("/ask", summary="Ask the autonomous knowledge agent")
async def ask_agent(body: AgentQuestionRequest) -> dict[str, Any]:
    """Answer a question with timeline, citations, and confidence."""
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    result = await _run_workflow(question)
    return {
        "answer": result.get("final_answer", ""),
        "timeline": result.get("timeline", []),
        "citations": result.get("citations", []),
        "confidence": result.get("confidence", 0.0),
        "processing_logs": result.get("processing_logs", []),
        "errors": result.get("errors", []),
    }


@router.post("/document", summary="Generate evidence-based documentation")
async def generate_documentation(body: AgentDocumentRequest) -> dict[str, Any]:
    """Create an ADR, meeting summary, and release notes for a feature."""
    feature = body.feature.strip()
    if not feature:
        raise HTTPException(status_code=400, detail="Feature cannot be empty.")
    result = await _run_workflow(f"Generate documentation for {feature}.")
    return {
        "feature": feature,
        "documents": result.get("generated_documentation", {}),
        "citations": result.get("citations", []),
        "confidence": result.get("confidence", 0.0),
        "processing_logs": result.get("processing_logs", []),
        "errors": result.get("errors", []),
    }


@router.get("/workflow", summary="View the executable agent workflow")
def get_workflow() -> dict[str, list[str]]:
    """Return the ordered execution plan, including the optional branch."""
    return workflow_visualization()


@router.get("/status", summary="Get multi-agent service status")
def get_agent_status() -> dict[str, Any]:
    """Return static readiness metadata without triggering models or retrieval."""
    return {
        "status": "ready",
        "workflow_timeout_seconds": WORKFLOW_TIMEOUT_SECONDS,
        "agents": [
            "coordinator",
            "context",
            "timeline",
            "reasoning",
            "citation",
            "documentation",
        ],
    }


@router.get("/sample", summary="Run a sample multi-agent question")
async def run_sample() -> dict[str, Any]:
    """Run the PostgreSQL decision question through the entire workflow."""
    return await ask_agent(AgentQuestionRequest(question=SAMPLE_QUESTION))
