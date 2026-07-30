"""
citation_builder.py

Parses retrieved Knowledge Nodes and builds structured citation objects
to be returned alongside every LLM answer.
"""

from typing import List
from app.rag.retriever import RetrievedNode


class Citation:
    def __init__(self, platform: str, title: str, feature: str):
        self.platform = platform
        self.title = title
        self.feature = feature

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "title": self.title,
            "feature": self.feature,
        }


def _extract_citations_from_document(document: str, feature: str) -> List[Citation]:
    """
    Parse the plain-text Knowledge Node document and extract per-platform citations.
    Looks for platform section headers written by ingestion.py.
    """
    citations: List[Citation] = []
    platform_map = {
        "Slack Discussions:": "Slack",
        "Jira Tickets:": "Jira",
        "GitHub Events:": "GitHub",
        "Notion Documents:": "Notion",
    }

    lines = document.splitlines()
    current_platform = None

    for line in lines:
        stripped = line.strip()
        if stripped in platform_map:
            current_platform = platform_map[stripped]
            continue
        if current_platform and stripped.startswith("- "):
            title = stripped[2:].split(":")[0].strip()  # take text before ":"
            if title:
                citations.append(Citation(
                    platform=current_platform,
                    title=title,
                    feature=feature,
                ))

    return citations


def build_citations(nodes: List[RetrievedNode]) -> List[dict]:
    """
    Build the full list of citations across all retrieved nodes.
    Deduplicates by (platform, title) pair.
    """
    seen: set = set()
    result: List[dict] = []

    for node in nodes:
        node_citations = _extract_citations_from_document(node.document, node.feature)
        for c in node_citations:
            key = (c.platform, c.title)
            if key not in seen:
                seen.add(key)
                result.append(c.to_dict())

    return result
