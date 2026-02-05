"""Canonical data schemas for Neural Express."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class NewsItem:
    """Canonical news item schema."""
    id: str                           # stable hash of url
    source: str                       # "rss" | "arxiv"
    source_name: str                  # "TechCrunch", "MIT Tech Review"
    title: str
    url: str
    published_at: datetime            # ISO8601
    author: Optional[str]
    summary_raw: str                  # from source
    content_snippet: str              # first ~500 chars
    tags: list[str] = field(default_factory=list)
    engagement: dict = field(default_factory=dict)
    duplicates: list[str] = field(default_factory=list)  # URLs of duplicate articles
    story_chain_id: Optional[str] = None  # Links related stories across days


@dataclass
class ImageSuggestion:
    """Image suggestion for a story."""
    search_keywords: list[str]        # 3-6 keywords
    credit_line: str                  # "Image source: Microsoft"
    source_url: Optional[str] = None  # official image URL if known
    fallback_banner: bool = False     # True if no official source


@dataclass
class StorySummary:
    """LLM-generated story summary."""
    headline: str                     # refined title
    hook: str                         # 1-2 line intro
    details: list[str]                # 3-6 bullets
    why_it_matters: str               # 2-4 lines
    category: str                     # Chips|Research|Policy|Tools|Business|Funding
    image_suggestion: ImageSuggestion


@dataclass
class RankedStory:
    """News item with ranking score."""
    news_item: NewsItem
    score: float
    recency_score: float
    credibility_score: float
    engagement_score: float
    uniqueness_score: float
    relevance_score: float
    summary: Optional[StorySummary] = None
