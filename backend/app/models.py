"""
models.py

SQLAlchemy ORM models mapping to the existing PostgreSQL tables in
knowledge_agent_db.

Relationship graph:

    Project
      ├── TeamMember      (one-to-many)
      ├── SlackMessage    (one-to-many)
      ├── JiraTicket      (one-to-many)
      ├── GithubEvent     (one-to-many)
      └── NotionDocument  (one-to-many)

    TeamMember
      ├── SlackMessage    (one-to-many, via member_id)
      ├── JiraTicket      (one-to-many, via assignee_id)
      ├── GithubEvent     (one-to-many, via member_id)
      └── NotionDocument  (one-to-many, via author_id)

These relationships allow joined queries such as "get all Slack messages
with the author's name" or "get the full project graph in one query",
which the future RAG / Knowledge Agent phases will rely on heavily.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, nullable=False)
    company_name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    team_members = relationship(
        "TeamMember", back_populates="project", cascade="all, delete-orphan"
    )
    slack_messages = relationship(
        "SlackMessage", back_populates="project", cascade="all, delete-orphan"
    )
    jira_tickets = relationship(
        "JiraTicket", back_populates="project", cascade="all, delete-orphan"
    )
    github_events = relationship(
        "GithubEvent", back_populates="project", cascade="all, delete-orphan"
    )
    notion_documents = relationship(
        "NotionDocument", back_populates="project", cascade="all, delete-orphan"
    )


class TeamMember(Base):
    __tablename__ = "team_members"

    member_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=True)
    email = Column(String, nullable=True)
    department = Column(String, nullable=True)
    joined_date = Column(Date, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="team_members")
    slack_messages = relationship("SlackMessage", back_populates="member")
    jira_tickets = relationship(
        "JiraTicket",
        back_populates="assignee",
        foreign_keys="JiraTicket.assignee_id",
    )
    github_events = relationship("GithubEvent", back_populates="member")
    notion_documents = relationship("NotionDocument", back_populates="author")


class SlackMessage(Base):
    __tablename__ = "slack_messages"

    message_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    member_id = Column(Integer, ForeignKey("team_members.member_id"), nullable=True)
    channel_name = Column(String, nullable=True)
    thread_id = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    message_time = Column(DateTime, nullable=True)
    related_feature = Column(String, nullable=True, index=True)

    # Relationships
    project = relationship("Project", back_populates="slack_messages")
    member = relationship("TeamMember", back_populates="slack_messages")


class JiraTicket(Base):
    __tablename__ = "jira_tickets"

    jira_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("team_members.member_id"), nullable=True)
    ticket_number = Column(String, nullable=True)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    related_feature = Column(String, nullable=True, index=True)

    # Relationships
    project = relationship("Project", back_populates="jira_tickets")
    assignee = relationship(
        "TeamMember",
        back_populates="jira_tickets",
        foreign_keys=[assignee_id],
    )


class GithubEvent(Base):
    __tablename__ = "github_events"

    github_event_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    member_id = Column(Integer, ForeignKey("team_members.member_id"), nullable=True)
    event_type = Column(String, nullable=True)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    event_time = Column(DateTime, nullable=True)
    branch_name = Column(String, nullable=True)
    related_feature = Column(String, nullable=True, index=True)

    # Relationships
    project = relationship("Project", back_populates="github_events")
    member = relationship("TeamMember", back_populates="github_events")


class NotionDocument(Base):
    __tablename__ = "notion_documents"

    document_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    author_id = Column(Integer, ForeignKey("team_members.member_id"), nullable=True)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    related_feature = Column(String, nullable=True, index=True)

    # Relationships
    project = relationship("Project", back_populates="notion_documents")
    author = relationship("TeamMember", back_populates="notion_documents")
