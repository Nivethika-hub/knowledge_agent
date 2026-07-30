"""
timeline_builder.py

Aggregates multiple platform events into a single, unified, chronological timeline.
Ensures that events from Slack, Jira, GitHub, and Notion are correctly interleaved.
"""

from typing import List
from app.knowledge.knowledge_models import TimelineEvent
from app.models import SlackMessage, JiraTicket, GithubEvent, NotionDocument

def build_feature_timeline(
    slack_msgs: List[SlackMessage],
    jira_tickets: List[JiraTicket],
    github_events: List[GithubEvent],
    notion_docs: List[NotionDocument]
) -> List[TimelineEvent]:
    events = []
    
    for msg in slack_msgs:
        if msg.message_time:
            events.append(TimelineEvent(
                platform="Slack",
                timestamp=msg.message_time,
                title=f"Slack Discussion in {msg.channel_name or 'thread'}",
                description=msg.message or ""
            ))
            
    for ticket in jira_tickets:
        if ticket.created_at:
            events.append(TimelineEvent(
                platform="Jira",
                timestamp=ticket.created_at,
                title=f"Jira Ticket: {ticket.title or ticket.ticket_number}",
                description=ticket.description or ""
            ))
            
    for event in github_events:
        if event.event_time:
            events.append(TimelineEvent(
                platform="GitHub",
                timestamp=event.event_time,
                title=f"GitHub Event: {event.title or event.event_type}",
                description=event.description or ""
            ))
            
    for doc in notion_docs:
        if doc.updated_at:
            events.append(TimelineEvent(
                platform="Notion",
                timestamp=doc.updated_at,
                title=f"Notion Document: {doc.title}",
                description=doc.content or ""
            ))
            
    # Sort chronologically (oldest to newest)
    events.sort(key=lambda x: x.timestamp)
    return events
