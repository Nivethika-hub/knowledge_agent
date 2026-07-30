"""
knowledge_models.py

Pydantic models for structured Knowledge Nodes.
These models represent the refined output after transforming raw
database platform data (Slack, Jira, GitHub, Notion) into cohesive insights.
"""

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class Participant(BaseModel):
    member_id: int
    full_name: str
    role: Optional[str] = None

class Evidence(BaseModel):
    platform: str
    content: str
    url_or_id: str

class TimelineEvent(BaseModel):
    platform: str
    timestamp: datetime
    title: str
    description: str

class KnowledgeNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    feature_name: str
    decision: str
    reason: str
    participants: List[Participant]
    timeline: List[TimelineEvent]
    
    # Raw references (text or IDs) for provenance
    slack_messages: List[str]
    jira_tickets: List[str]
    github_events: List[str]
    notion_documents: List[str]
    
    generated_at: datetime
