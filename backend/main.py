"""
main.py

Entry point for the Autonomous Context-Bridging Knowledge Agent backend.

Run with:
    uvicorn main:app --reload

Swagger docs available at:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from routes import (
    agent,
    ask,
    automation,
    github,
    jira,
    knowledge,
    notion,
    notifications,
    projects,
    slack,
    team_members,
    vector,
)

app = FastAPI(
    title="Autonomous Context-Bridging Knowledge Agent",
    description=(
        "Backend REST API that unifies Slack, Jira, GitHub, and Notion "
        "data for a project, so an AI Knowledge Agent / RAG pipeline can "
        "answer cross-platform questions such as 'why did we choose "
        "PostgreSQL?' or 'what is the timeline of feature X?'."
    ),
    version="1.0.0",
)

# ----------------------------------------------------------------------
# CORS - open for local hackathon development; tighten before production.
# ----------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------------
# Global exception handler for anything unhandled -> clean 500 response
# ----------------------------------------------------------------------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {exc}"},
    )


# ----------------------------------------------------------------------
# Routers
# ----------------------------------------------------------------------
app.include_router(projects.router)
app.include_router(team_members.router)
app.include_router(slack.router)
app.include_router(jira.router)
app.include_router(github.router)
app.include_router(notion.router)
app.include_router(notifications.router)
app.include_router(knowledge.router)
app.include_router(vector.router)
app.include_router(ask.router)
app.include_router(agent.router)
app.include_router(automation.router)


@app.get("/", tags=["Health"], summary="Health check")
def root():
    return {"status": "ok", "service": "Autonomous Context-Bridging Knowledge Agent"}
