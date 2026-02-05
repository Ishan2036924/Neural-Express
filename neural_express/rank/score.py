"""Scoring functions for ranking news items."""

from datetime import datetime, timedelta
import re

from ..utils.schema import NewsItem
from ..utils.logging import get_logger

logger = get_logger("rank.score")


def calculate_recency_score(
    item: NewsItem,
    time_window_hours: int = 24
) -> float:
    """
    Calculate recency score (1.0 if within window, decay after).

    Args:
        item: News item
        time_window_hours: Time window in hours (24 for daily, 168 for weekly)

    Returns:
        Score between 0 and 1
    """
    now = datetime.now()
    age_hours = (now - item.published_at).total_seconds() / 3600

    if age_hours < 0:
        age_hours = 0

    if age_hours <= time_window_hours:
        return 1.0

    # Exponential decay after time window
    decay_rate = 0.1
    excess_hours = age_hours - time_window_hours
    score = 1.0 * (0.5 ** (excess_hours / (time_window_hours * decay_rate)))

    return max(0.0, min(1.0, score))


def calculate_credibility_score(item: NewsItem) -> float:
    """
    Calculate credibility score based on source.

    Args:
        item: News item

    Returns:
        Score between 0 and 1
    """
    return item.engagement.get("credibility", 0.5)


def calculate_engagement_score(item: NewsItem) -> float:
    """
    Calculate engagement score (placeholder for future metrics).

    Args:
        item: News item

    Returns:
        Score between 0 and 1
    """
    # Future: incorporate upvotes, comments, shares, etc.
    # For now, return neutral score
    return 0.5


def calculate_uniqueness_score(item: NewsItem) -> float:
    """
    Calculate uniqueness score based on cluster size.

    Args:
        item: News item (with duplicates list)

    Returns:
        Score between 0 and 1
    """
    cluster_size = len(item.duplicates) + 1  # +1 for the item itself

    # Score is inverse of cluster size (more unique = higher score)
    score = 1.0 / cluster_size

    return score


def calculate_relevance_score(
    item: NewsItem,
    keywords: list[str]
) -> float:
    """
    Calculate relevance score based on keyword density.

    Args:
        item: News item
        keywords: List of relevance keywords

    Returns:
        Score between 0 and 1
    """
    # Combine title and content for analysis
    text = f"{item.title} {item.content_snippet}".lower()

    # Count keyword matches
    matches = 0
    for keyword in keywords:
        if keyword.lower() in text:
            matches += 1

    # Calculate density
    if not keywords:
        return 0.5

    density = matches / len(keywords)

    # Normalize to 0-1 range (cap at 5 matches)
    score = min(1.0, density * 2)

    return score


def calculate_composite_score(
    item: NewsItem,
    weights: dict,
    time_window_hours: int,
    relevance_keywords: list[str]
) -> dict:
    """
    Calculate composite score with all components.

    Args:
        item: News item
        weights: Weight dict with keys: recency, credibility, engagement, uniqueness, relevance
        time_window_hours: Time window for recency calculation
        relevance_keywords: Keywords for relevance scoring

    Returns:
        Dict with overall score and component scores
    """
    # Calculate component scores
    recency = calculate_recency_score(item, time_window_hours)
    credibility = calculate_credibility_score(item)
    engagement = calculate_engagement_score(item)
    uniqueness = calculate_uniqueness_score(item)
    relevance = calculate_relevance_score(item, relevance_keywords)

    # Calculate weighted sum
    score = (
        weights.get("recency", 0.3) * recency +
        weights.get("credibility", 0.25) * credibility +
        weights.get("engagement", 0.15) * engagement +
        weights.get("uniqueness", 0.15) * uniqueness +
        weights.get("relevance", 0.15) * relevance
    )

    return {
        "score": score,
        "recency_score": recency,
        "credibility_score": credibility,
        "engagement_score": engagement,
        "uniqueness_score": uniqueness,
        "relevance_score": relevance
    }
