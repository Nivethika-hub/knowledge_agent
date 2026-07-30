"""
feature_search.py

Contains reusable SQLAlchemy queries to fetch evidence across all platforms
(Slack, Jira, GitHub, Notion) tied to a specific feature name.
"""

from sqlalchemy.orm import Session
from app.models import SlackMessage, JiraTicket, GithubEvent, NotionDocument, TeamMember

def get_slack_by_feature(db: Session, feature_name: str) -> list[SlackMessage]:
    return db.query(SlackMessage).filter(SlackMessage.related_feature == feature_name).all()

def get_jira_by_feature(db: Session, feature_name: str) -> list[JiraTicket]:
    return db.query(JiraTicket).filter(JiraTicket.related_feature == feature_name).all()

def get_github_by_feature(db: Session, feature_name: str) -> list[GithubEvent]:
    return db.query(GithubEvent).filter(GithubEvent.related_feature == feature_name).all()

def get_notion_by_feature(db: Session, feature_name: str) -> list[NotionDocument]:
    return db.query(NotionDocument).filter(NotionDocument.related_feature == feature_name).all()

def get_team_members_by_feature(db: Session, feature_name: str) -> list[TeamMember]:
    """
    Collects unique members involved in a feature across all platforms.
    """
    slack_members = db.query(TeamMember).join(SlackMessage).filter(SlackMessage.related_feature == feature_name).all()
    jira_members = db.query(TeamMember).join(JiraTicket).filter(JiraTicket.related_feature == feature_name).all()
    github_members = db.query(TeamMember).join(GithubEvent).filter(GithubEvent.related_feature == feature_name).all()
    notion_members = db.query(TeamMember).join(NotionDocument).filter(NotionDocument.related_feature == feature_name).all()
    
    unique_members = {m.member_id: m for m in (slack_members + jira_members + github_members + notion_members)}
    return list(unique_members.values())

def search_feature(db: Session, feature_name: str) -> dict:
    """
    Search every platform and return a dictionary containing related records.
    """
    return {
        "slack": get_slack_by_feature(db, feature_name),
        "jira": get_jira_by_feature(db, feature_name),
        "github": get_github_by_feature(db, feature_name),
        "notion": get_notion_by_feature(db, feature_name),
        "members": get_team_members_by_feature(db, feature_name)
    }
