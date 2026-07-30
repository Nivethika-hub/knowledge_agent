"""
schemas.py

Pydantic schemas used for request validation and response serialization.

For every table we define:
    - <Name>Base     shared fields
    - <Name>Create   fields required to create a new row
    - <Name>Update   all fields optional, used for PATCH/PUT
    - <Name>Response  full object returned to the client (includes IDs)

Pydantic v2 style (`model_config = ConfigDict(from_attributes=True)`) is
used so schemas can be built directly from SQLAlchemy ORM objects.
"""

from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, EmailStr


# ============================================================
# PROJECT
# ============================================================
class ProjectBase(BaseModel):
    project_name: str
    company_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    company_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    project_id: int
    created_at: Optional[datetime] = None


# ============================================================
# TEAM MEMBER
# ============================================================
class TeamMemberBase(BaseModel):
    project_id: int
    full_name: str
    role: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    joined_date: Optional[date] = None


class TeamMemberCreate(TeamMemberBase):
    pass


class TeamMemberUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    joined_date: Optional[date] = None


class TeamMemberResponse(TeamMemberBase):
    model_config = ConfigDict(from_attributes=True)

    member_id: int


# ============================================================
# SLACK MESSAGE
# ============================================================
class SlackMessageBase(BaseModel):
    project_id: int
    member_id: Optional[int] = None
    channel_name: Optional[str] = None
    thread_id: Optional[int] = None
    message: Optional[str] = None
    message_time: Optional[datetime] = None
    related_feature: Optional[str] = None


class SlackMessageCreate(SlackMessageBase):
    pass


class SlackMessageUpdate(BaseModel):
    channel_name: Optional[str] = None
    thread_id: Optional[int] = None
    message: Optional[str] = None
    message_time: Optional[datetime] = None
    related_feature: Optional[str] = None


class SlackMessageResponse(SlackMessageBase):
    model_config = ConfigDict(from_attributes=True)

    message_id: int


# ============================================================
# JIRA TICKET
# ============================================================
class JiraTicketBase(BaseModel):
    project_id: int
    assignee_id: Optional[int] = None
    ticket_number: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    related_feature: Optional[str] = None


class JiraTicketCreate(JiraTicketBase):
    pass


class JiraTicketUpdate(BaseModel):
    ticket_number: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    completed_at: Optional[datetime] = None
    related_feature: Optional[str] = None


class JiraTicketResponse(JiraTicketBase):
    model_config = ConfigDict(from_attributes=True)

    jira_id: int


# ============================================================
# GITHUB EVENT
# ============================================================
class GithubEventBase(BaseModel):
    project_id: int
    member_id: Optional[int] = None
    event_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    event_time: Optional[datetime] = None
    branch_name: Optional[str] = None
    related_feature: Optional[str] = None


class GithubEventCreate(GithubEventBase):
    pass


class GithubEventUpdate(BaseModel):
    event_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    event_time: Optional[datetime] = None
    branch_name: Optional[str] = None
    related_feature: Optional[str] = None


class GithubEventResponse(GithubEventBase):
    model_config = ConfigDict(from_attributes=True)

    github_event_id: int


# ============================================================
# NOTION DOCUMENT
# ============================================================
class NotionDocumentBase(BaseModel):
    project_id: int
    author_id: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    updated_at: Optional[datetime] = None
    related_feature: Optional[str] = None


class NotionDocumentCreate(NotionDocumentBase):
    pass


class NotionDocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    updated_at: Optional[datetime] = None
    related_feature: Optional[str] = None


class NotionDocumentResponse(NotionDocumentBase):
    model_config = ConfigDict(from_attributes=True)

    document_id: int


# ============================================================
# KNOWLEDGE / AI-READY COMPOSITE SCHEMAS
# ============================================================
class FeatureKnowledgeResponse(BaseModel):
    """Combined view of everything related to a single feature."""

    related_feature: str
    slack_messages: List[SlackMessageResponse] = []
    jira_tickets: List[JiraTicketResponse] = []
    github_events: List[GithubEventResponse] = []
    notion_documents: List[NotionDocumentResponse] = []


class TimelineEvent(BaseModel):
    """A single normalized event in a project's chronological timeline."""

    source: str  # "slack" | "jira" | "github" | "notion"
    timestamp: Optional[datetime] = None
    title: Optional[str] = None
    detail: Optional[str] = None
    related_feature: Optional[str] = None
    raw_id: int


class ProjectTimelineResponse(BaseModel):
    project_id: int
    project_name: Optional[str] = None
    total_events: int
    timeline: List[TimelineEvent]
