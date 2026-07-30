"""
knowledge_generator.py

This module runs deterministic heuristic rules across the collected data 
from feature_search and timeline_builder to extract KnowledgeNodes.
No LLMs are used here (per Phase 4 rules).
"""

from datetime import datetime
from sqlalchemy.orm import Session

from app.knowledge.feature_search import search_feature
from app.knowledge.timeline_builder import build_feature_timeline
from app.knowledge.knowledge_models import KnowledgeNode, Participant

def extract_decision(slack_msgs: list) -> str:
    """Heuristic rule: check Slack for decision keywords."""
    keywords = ["approved", "selected", "decided", "finalized"]
    for msg in slack_msgs:
        if msg.message:
            text = msg.message.lower()
            if any(kw in text for kw in keywords):
                return msg.message
    return "No explicit decision found in Slack."

def extract_reasoning(notion_docs: list) -> str:
    """Heuristic rule: check Notion for reasoning keywords."""
    keywords = ["selected", "architecture", "decision", "reason"]
    for doc in notion_docs:
        if doc.content:
            text = doc.content.lower()
            if any(kw in text for kw in keywords):
                return doc.content
    return "No explicit reasoning found in Notion."

def generate_knowledge_node(db: Session, feature_name: str) -> KnowledgeNode:
    data = search_feature(db, feature_name)
    
    slack_msgs = data["slack"]
    jira_tickets = data["jira"]
    github_events = data["github"]
    notion_docs = data["notion"]
    members = data["members"]
    
    participants = []
    for m in members:
        participants.append(Participant(
            member_id=m.member_id,
            full_name=m.full_name,
            role=m.role
        ))
        
    timeline = build_feature_timeline(slack_msgs, jira_tickets, github_events, notion_docs)
    
    decision = extract_decision(slack_msgs)
    reasoning = extract_reasoning(notion_docs)
    
    return KnowledgeNode(
        feature_name=feature_name,
        decision=decision,
        reason=reasoning,
        participants=participants,
        timeline=timeline,
        slack_messages=[m.message for m in slack_msgs if m.message],
        jira_tickets=[f"{t.title}: {t.description}" for t in jira_tickets if t.title],
        github_events=[f"{e.title}: {e.description}" for e in github_events if e.title],
        notion_documents=[f"{d.title}: {d.content}" for d in notion_docs if d.title],
        generated_at=datetime.utcnow()
    )
