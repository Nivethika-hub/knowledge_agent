# 🧠 Autonomous Context-Bridging Knowledge Agent

> A production-ready FastAPI backend that unifies Slack, Jira, GitHub, and Notion data into a semantic knowledge graph — enabling an AI-powered RAG pipeline to answer complex, cross-platform questions about your project history.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Data Model](#data-model)
- [API Endpoints](#api-endpoints)
- [RAG Pipeline](#rag-pipeline)
- [Vector Search (ChromaDB)](#vector-search-chromadb)
- [Knowledge Nodes](#knowledge-nodes)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Running the Server](#running-the-server)
- [Roadmap](#roadmap)

---

## Overview

The **Autonomous Context-Bridging Knowledge Agent** is a backend service designed to eliminate information silos across development teams. It ingests raw data from four popular collaboration platforms (Slack, Jira, GitHub, Notion), synthesizes them into structured **Knowledge Nodes**, embeds them into a **ChromaDB** vector store, and exposes a full **RAG (Retrieval-Augmented Generation)** pipeline that can answer natural language questions like:

- *"Why did the team choose PostgreSQL?"*
- *"Who worked on the JWT Authentication feature?"*
- *"What is the complete timeline of the Dashboard feature?"*

---

## Key Features

| Feature | Description |
|---|---|
| 🔗 **Multi-Platform Ingestion** | CRUD APIs for Slack messages, Jira tickets, GitHub events, and Notion documents |
| 🧩 **Knowledge Node Synthesis** | Aggregates all platform signals for a feature into a single coherent node |
| 📅 **Timeline Builder** | Normalized, chronological cross-platform event timelines per project or feature |
| 🔍 **Semantic Search** | Sentence-transformer embeddings stored in ChromaDB for similarity retrieval |
| 🤖 **RAG Pipeline** | Groq LLM (via LangChain) answers natural language questions with source citations |
| 📚 **Citation Engine** | Every answer includes traceable citations back to original platform records |
| 🐞 **Debug Endpoint** | Full pipeline trace: retrieved nodes → prompt → raw LLM response |
| 📖 **Swagger UI** | Auto-generated interactive API docs at `/docs` |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Web Framework** | [FastAPI](https://fastapi.tiangolo.com/) 0.115 |
| **ASGI Server** | Uvicorn |
| **Database** | PostgreSQL (via SQLAlchemy 2.0 ORM + psycopg 3) |
| **Data Validation** | Pydantic v2 |
| **Vector Store** | [ChromaDB](https://www.trychroma.com/) ≥ 0.6.0 |
| **Embeddings** | [sentence-transformers](https://www.sbert.net/) ≥ 3.0.0 |
| **LLM** | [Groq](https://groq.com/) (via `langchain-groq`) |
| **LLM Orchestration** | [LangChain](https://www.langchain.com/) ≥ 0.3.0 |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                          │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │  Slack   │  │  Jira    │  │ GitHub   │  │   Notion     │   │
│  │  Routes  │  │  Routes  │  │  Routes  │  │   Routes     │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘   │
│       └─────────────┴─────────────┴────────────────┘           │
│                              │                                  │
│                     ┌────────▼─────────┐                       │
│                     │   PostgreSQL DB   │                       │
│                     │  (SQLAlchemy ORM) │                       │
│                     └────────┬─────────┘                       │
│                              │                                  │
│              ┌───────────────▼───────────────┐                 │
│              │      Knowledge Layer           │                 │
│              │  KnowledgeNode Generator       │                 │
│              │  Timeline Builder              │                 │
│              │  Feature Search                │                 │
│              └───────────────┬───────────────┘                 │
│                              │                                  │
│         ┌────────────────────▼──────────────────────┐          │
│         │             Vector Layer (Phase 5)         │          │
│         │  sentence-transformers → Embeddings        │          │
│         │  ChromaDB Vector Store                     │          │
│         │  Ingestion Pipeline | Retrieval Pipeline   │          │
│         └────────────────────┬──────────────────────┘          │
│                              │                                  │
│         ┌────────────────────▼──────────────────────┐          │
│         │             RAG Layer (Phase 6)            │          │
│         │  Retriever → Context Formatter             │          │
│         │  Prompt Builder → Groq LLM                 │          │
│         │  Answer Generator → Citation Builder       │          │
│         └────────────────────┬──────────────────────┘          │
│                              │                                  │
│              ┌───────────────▼──────────────┐                  │
│              │       /ask  Endpoints         │                  │
│              │  POST /ask  |  POST /ask/debug│                  │
│              └──────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
knowledge_agent/
└── backend/
    ├── main.py                     # FastAPI app entry point
    ├── requirements.txt
    ├── .env                        # Local environment variables
    ├── .env.example                # Template for env vars
    ├── .gitignore
    │
    ├── app/
    │   ├── database.py             # SQLAlchemy engine & session setup
    │   ├── models.py               # ORM models (Project, TeamMember, Slack, Jira, GitHub, Notion)
    │   ├── schemas.py              # Pydantic request/response schemas
    │   ├── crud.py                 # Generic CRUD operations
    │   ├── dependencies.py         # FastAPI dependency injectors (get_db)
    │   │
    │   ├── knowledge/              # Knowledge Layer
    │   │   ├── knowledge_models.py     # KnowledgeNode Pydantic model
    │   │   ├── knowledge_generator.py  # Builds KnowledgeNodes from DB
    │   │   ├── timeline_builder.py     # Cross-platform chronological timeline
    │   │   ├── feature_search.py       # Feature-level DB search
    │   │   └── ai_service.py           # AI utilities for knowledge layer
    │   │
    │   ├── vector/                 # Vector Layer (Phase 5)
    │   │   ├── chroma_client.py        # ChromaDB collection management
    │   │   ├── embedding_service.py    # sentence-transformers integration
    │   │   ├── vector_store.py         # Upsert / delete / get operations
    │   │   ├── ingestion.py            # Full & per-feature ingestion pipeline
    │   │   ├── retrieval.py            # Semantic search & similarity filtering
    │   │   └── similarity.py           # Cosine similarity helpers
    │   │
    │   └── rag/                    # RAG Layer (Phase 6)
    │       ├── rag_pipeline.py         # Public facade (run_pipeline / run_debug_pipeline)
    │       ├── retriever.py            # ChromaDB → KnowledgeNode dicts
    │       ├── context_formatter.py    # Format nodes into LLM context string
    │       ├── prompt_builder.py       # Builds the final LLM prompt
    │       ├── llm_service.py          # Groq LLM via LangChain
    │       ├── answer_generator.py     # Orchestrates retrieval + generation
    │       └── citation_builder.py     # Extracts source citations from answer
    │
    └── routes/
        ├── projects.py             # CRUD: Projects
        ├── team_members.py         # CRUD: Team Members
        ├── slack.py                # CRUD: Slack Messages
        ├── jira.py                 # CRUD: Jira Tickets
        ├── github.py               # CRUD: GitHub Events
        ├── notion.py               # CRUD: Notion Documents
        ├── knowledge.py            # Knowledge Node & Timeline endpoints
        ├── vector.py               # Semantic search & reindex endpoints
        └── ask.py                  # RAG Q&A endpoints (Phase 6)
```

---

## Data Model

The PostgreSQL schema is built around a central `Project`, with all platform data linked by both `project_id` and `member_id`. Every platform table tracks a `related_feature` field (indexed) to enable fast feature-scoped queries.

```
Project
  ├── TeamMember      (project_id FK)
  ├── SlackMessage    (project_id FK, member_id FK, related_feature)
  ├── JiraTicket      (project_id FK, assignee_id FK, related_feature)
  ├── GithubEvent     (project_id FK, member_id FK,  related_feature)
  └── NotionDocument  (project_id FK, author_id FK,  related_feature)
```

---

## API Endpoints

### 🏗️ Core CRUD

| Method | Path | Description |
|---|---|---|
| `GET/POST/PATCH/DELETE` | `/projects` | Manage projects |
| `GET/POST/PATCH/DELETE` | `/team-members` | Manage team members |
| `GET/POST/PATCH/DELETE` | `/slack` | Manage Slack messages |
| `GET/POST/PATCH/DELETE` | `/jira` | Manage Jira tickets |
| `GET/POST/PATCH/DELETE` | `/github` | Manage GitHub events |
| `GET/POST/PATCH/DELETE` | `/notion` | Manage Notion documents |

### 🧠 Knowledge Layer

| Method | Path | Description |
|---|---|---|
| `GET` | `/knowledge/features/{project_id}` | List all features in a project |
| `GET` | `/knowledge/node/{project_id}/{feature}` | Get full KnowledgeNode for a feature |
| `GET` | `/knowledge/timeline/{project_id}` | Chronological cross-platform timeline |

### 🔍 Semantic Search (Vector Layer)

| Method | Path | Description |
|---|---|---|
| `GET` | `/vector/search?q=...` | Semantic search over Knowledge Nodes |
| `POST` | `/vector/reindex` | Rebuild full ChromaDB index from DB |
| `POST` | `/vector/reindex/{feature_name}` | Reindex a single feature |
| `GET` | `/vector/count` | Total number of indexed documents |
| `GET` | `/vector/features` | List all indexed feature names |

### 🤖 RAG — Question Answering

| Method | Path | Description |
|---|---|---|
| `POST` | `/ask` | Ask a natural-language question |
| `GET` | `/ask/sample` | Run a preset sample question |
| `GET` | `/ask/history` | Get recent Q&A session history |
| `POST` | `/ask/debug` | Full pipeline trace for debugging |

> 📖 Interactive documentation available at **`http://127.0.0.1:8000/docs`**

---

## RAG Pipeline

The `/ask` endpoint runs a 4-stage pipeline:

```
User Question
     │
     ▼
1. Retriever         — Embeds question → semantic search in ChromaDB → top-K KnowledgeNodes
     │
     ▼
2. Context Formatter — Converts KnowledgeNode dicts into a structured text context
     │
     ▼
3. Prompt Builder    — Combines system instructions + context + user question into a final prompt
     │
     ▼
4. Groq LLM          — Generates answer via langchain-groq; citation_builder extracts sources
     │
     ▼
Structured JSON Response: { answer, citations, nodes_used, question }
```

The `/ask/debug` endpoint returns the full trace at every stage — retrieved nodes, formatted context, the exact prompt, and the raw LLM response — for development and evaluation.

---

## Vector Search (ChromaDB)

Knowledge Nodes are converted into embedding vectors using `sentence-transformers` and stored in ChromaDB:

- **Embedding model**: `sentence-transformers` (configurable)
- **Collection**: per-project ChromaDB collection
- **Metadata stored**: `feature_name`, `decision`, `participants`, source counts
- **Idempotent upserts**: safe to reindex without duplicating records
- **Similarity filtering**: optional `threshold` parameter on `/vector/search`

---

## Knowledge Nodes

A `KnowledgeNode` is the core unit of the system — a synthesized, AI-ready snapshot of everything known about a specific feature:

```python
class KnowledgeNode:
    feature_name: str          # e.g. "JWT Authentication"
    decision: str              # What was decided
    reason: str                # Why it was decided
    participants: List[Participant]
    timeline: List[TimelineEvent]
    slack_messages: List[str]  # Raw provenance references
    jira_tickets: List[str]
    github_events: List[str]
    notion_documents: List[str]
    generated_at: datetime
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- A [Groq API key](https://console.groq.com/) (free tier available)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd knowledge_agent/backend
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your values
```

### 5. Create the PostgreSQL database

```sql
CREATE DATABASE knowledge_agent_db;
```

The ORM will auto-create all tables on first startup.

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_NAME` | Database name | `knowledge_agent_db` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | *(required)* |
| `GROQ_API_KEY` | Groq API key for LLM | *(required for /ask)* |

---

## Running the Server

```bash
# From the backend/ directory
uvicorn main:app --reload
```

The API will be available at:
- **Base URL**: `http://127.0.0.1:8000`
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### First-time setup: populate and index data

```bash
# 1. Add a project via POST /projects
# 2. Add platform data via POST /slack, /jira, /github, /notion
# 3. Build the vector index:
curl -X POST http://127.0.0.1:8000/vector/reindex

# 4. Ask a question:
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Why did the team choose PostgreSQL?", "top_k": 5}'
```

---

## Roadmap

| Phase | Status | Description |
|---|---|---|
| Phase 1 | ✅ Complete | PostgreSQL schema + SQLAlchemy ORM + Pydantic schemas |
| Phase 2 | ✅ Complete | CRUD REST APIs for all 6 entities |
| Phase 3 | ✅ Complete | Knowledge Layer — feature search, timeline builder |
| Phase 4 | ✅ Complete | KnowledgeNode synthesis — cross-platform aggregation |
| Phase 5 | ✅ Complete | Vector Layer — embeddings, ChromaDB ingestion & retrieval |
| Phase 6 | ✅ Complete | RAG Pipeline — Groq LLM + citation engine + /ask API |
| Phase 7 | 🔜 Planned | Persistent conversation history + multi-turn memory |
| Phase 8 | 🔜 Planned | Autonomous agents for proactive knowledge updates |

---

## License

This project is open-source. Feel free to extend, modify, and build upon it.

---

*Built with FastAPI, ChromaDB, sentence-transformers, and Groq. Designed for developer teams who want answers, not more dashboards.*
