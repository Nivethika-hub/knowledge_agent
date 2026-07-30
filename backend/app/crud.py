"""
crud.py

Reusable data-access functions. Routes call into this module rather than
querying the ORM directly, keeping business logic separate from the
HTTP layer (easier to unit test and reuse in the future RAG pipeline).
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app import models


# ============================================================
# PROJECTS
# ============================================================
def get_all_projects(db: Session, skip: int = 0, limit: int = 100) -> List[models.Project]:
    return db.query(models.Project).offset(skip).limit(limit).all()


def get_project_by_id(db: Session, project_id: int) -> Optional[models.Project]:
    return (
        db.query(models.Project)
        .filter(models.Project.project_id == project_id)
        .first()
    )


def create_project(db: Session, project_data: dict) -> models.Project:
    project = models.Project(**project_data)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


# ============================================================
# TEAM MEMBERS
# ============================================================
def get_team_members(
    db: Session, project_id: Optional[int] = None, skip: int = 0, limit: int = 100
) -> List[models.TeamMember]:
    query = db.query(models.TeamMember)
    if project_id is not None:
        query = query.filter(models.TeamMember.project_id == project_id)
    return query.offset(skip).limit(limit).all()


def get_team_member_by_id(db: Session, member_id: int) -> Optional[models.TeamMember]:
    return (
        db.query(models.TeamMember)
        .filter(models.TeamMember.member_id == member_id)
        .first()
    )


# ============================================================
# SLACK MESSAGES
# ============================================================
def get_slack_messages(
    db: Session, project_id: Optional[int] = None, skip: int = 0, limit: int = 100
) -> List[models.SlackMessage]:
    query = db.query(models.SlackMessage)
    if project_id is not None:
        query = query.filter(models.SlackMessage.project_id == project_id)
    return query.offset(skip).limit(limit).all()


# ============================================================
# JIRA TICKETS
# ============================================================
def get_jira_tickets(
    db: Session, project_id: Optional[int] = None, skip: int = 0, limit: int = 100
) -> List[models.JiraTicket]:
    query = db.query(models.JiraTicket)
    if project_id is not None:
        query = query.filter(models.JiraTicket.project_id == project_id)
    return query.offset(skip).limit(limit).all()


# ============================================================
# GITHUB EVENTS
# ============================================================
def get_github_events(
    db: Session, project_id: Optional[int] = None, skip: int = 0, limit: int = 100
) -> List[models.GithubEvent]:
    query = db.query(models.GithubEvent)
    if project_id is not None:
        query = query.filter(models.GithubEvent.project_id == project_id)
    return query.offset(skip).limit(limit).all()


# ============================================================
# NOTION DOCUMENTS
# ============================================================
def get_notion_documents(
    db: Session, project_id: Optional[int] = None, skip: int = 0, limit: int = 100
) -> List[models.NotionDocument]:
    query = db.query(models.NotionDocument)
    if project_id is not None:
        query = query.filter(models.NotionDocument.project_id == project_id)
    return query.offset(skip).limit(limit).all()


# ============================================================
# CROSS-SOURCE "KNOWLEDGE" HELPERS
# ============================================================
def get_messages_by_feature(db: Session, feature_name: str) -> List[models.SlackMessage]:
    """Slack messages tagged with a given related_feature."""
    return (
        db.query(models.SlackMessage)
        .filter(models.SlackMessage.related_feature.ilike(feature_name))
        .all()
    )


def search_feature(db: Session, feature_name: str) -> dict:
    """
    Pull every record (Slack, Jira, GitHub, Notion) tagged with the given
    related_feature, across all sources. Case-insensitive match.
    """
    slack = (
        db.query(models.SlackMessage)
        .filter(models.SlackMessage.related_feature.ilike(feature_name))
        .all()
    )
    jira = (
        db.query(models.JiraTicket)
        .filter(models.JiraTicket.related_feature.ilike(feature_name))
        .all()
    )
    github = (
        db.query(models.GithubEvent)
        .filter(models.GithubEvent.related_feature.ilike(feature_name))
        .all()
    )
    notion = (
        db.query(models.NotionDocument)
        .filter(models.NotionDocument.related_feature.ilike(feature_name))
        .all()
    )

    return {
        "slack_messages": slack,
        "jira_tickets": jira,
        "github_events": github,
        "notion_documents": notion,
    }


def get_project_timeline(db: Session, project_id: int) -> Optional[dict]:
    """
    Build a unified, chronologically sorted timeline for a project by
    merging Slack messages, Jira tickets, GitHub events, and Notion
    documents into a single normalized list of events.
    """
    project = get_project_by_id(db, project_id)
    if project is None:
        return None

    events = []

    for msg in db.query(models.SlackMessage).filter(
        models.SlackMessage.project_id == project_id
    ):
        events.append(
            {
                "source": "slack",
                "timestamp": msg.message_time,
                "title": f"Slack message in #{msg.channel_name}" if msg.channel_name else "Slack message",
                "detail": msg.message,
                "related_feature": msg.related_feature,
                "raw_id": msg.message_id,
            }
        )

    for ticket in db.query(models.JiraTicket).filter(
        models.JiraTicket.project_id == project_id
    ):
        events.append(
            {
                "source": "jira",
                "timestamp": ticket.created_at,
                "title": ticket.title or ticket.ticket_number,
                "detail": ticket.description,
                "related_feature": ticket.related_feature,
                "raw_id": ticket.jira_id,
            }
        )

    for gh in db.query(models.GithubEvent).filter(
        models.GithubEvent.project_id == project_id
    ):
        events.append(
            {
                "source": "github",
                "timestamp": gh.event_time,
                "title": gh.title or gh.event_type,
                "detail": gh.description,
                "related_feature": gh.related_feature,
                "raw_id": gh.github_event_id,
            }
        )

    for doc in db.query(models.NotionDocument).filter(
        models.NotionDocument.project_id == project_id
    ):
        events.append(
            {
                "source": "notion",
                "timestamp": doc.updated_at,
                "title": doc.title,
                "detail": doc.content,
                "related_feature": doc.related_feature,
                "raw_id": doc.document_id,
            }
        )

    # Sort chronologically. Events with no timestamp are pushed to the end.
    events.sort(
        key=lambda e: (e["timestamp"] is None, e["timestamp"])
    )

    return {
        "project_id": project.project_id,
        "project_name": project.project_name,
        "total_events": len(events),
        "timeline": events,
    }
