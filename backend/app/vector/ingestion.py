"""
ingestion.py

Reads every Knowledge Node from Phase 4, converts it to plain text,
generates an embedding, and stores it in ChromaDB.
"""

from sqlalchemy.orm import Session
from app.knowledge.ai_service import build_knowledge_node, get_all_features
from app.knowledge.knowledge_models import KnowledgeNode
from app.vector.vector_store import insert_node, insert_nodes
from typing import Optional


def knowledge_node_to_text(node: KnowledgeNode) -> str:
    """Convert a KnowledgeNode into a single plain-text document for embedding."""
    participant_names = ", ".join(p.full_name for p in node.participants)
    timeline_lines = "\n".join(
        f"  {e.timestamp.strftime('%H:%M')} [{e.platform}] {e.title}"
        for e in node.timeline
    )
    text = (
        f"Feature:\n{node.feature_name}\n\n"
        f"Decision:\n{node.decision}\n\n"
        f"Reason:\n{node.reason}\n\n"
        f"Participants:\n{participant_names}\n\n"
        f"Timeline:\n{timeline_lines}\n\n"
        f"Slack Discussions:\n" + "\n".join(f"  - {m}" for m in node.slack_messages) + "\n\n"
        f"Jira Tickets:\n" + "\n".join(f"  - {t}" for t in node.jira_tickets) + "\n\n"
        f"GitHub Events:\n" + "\n".join(f"  - {e}" for e in node.github_events) + "\n\n"
        f"Notion Documents:\n" + "\n".join(f"  - {d}" for d in node.notion_documents)
    )
    return text


def metadata_builder(node: KnowledgeNode) -> dict:
    """Build a flat metadata dict for ChromaDB."""
    return {
        "feature_name": node.feature_name,
        "decision": node.decision,
        "participants": [p.full_name for p in node.participants],
        "generated_at": node.generated_at.isoformat(),
    }


def ingest_feature(db: Session, feature_name: str) -> dict:
    """
    Generate a Knowledge Node for one feature and insert it into ChromaDB.
    Returns a status dict.
    """
    node = build_knowledge_node(db, feature_name)
    doc_id = feature_name.strip().lower().replace(" ", "_")
    text = knowledge_node_to_text(node)
    metadata = metadata_builder(node)
    insert_node(doc_id, text, metadata)
    return {"status": "indexed", "feature": feature_name, "doc_id": doc_id}


def ingest_all_knowledge_nodes(db: Session) -> dict:
    """
    Iterate over every unique feature in the database,
    generate Knowledge Nodes and batch-insert them into ChromaDB.
    """
    features = get_all_features(db)
    if not features:
        return {"status": "no_features", "indexed": 0}

    batch = []
    for feature_name in features:
        if not feature_name:
            continue
        node = build_knowledge_node(db, feature_name)
        doc_id = feature_name.strip().lower().replace(" ", "_")
        text = knowledge_node_to_text(node)
        metadata = metadata_builder(node)
        batch.append({"id": doc_id, "text": text, "metadata": metadata})

    insert_nodes(batch)
    return {"status": "ok", "indexed": len(batch), "features": [b["id"] for b in batch]}
