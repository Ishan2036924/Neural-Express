"""Story selection logic."""

from ..utils.schema import NewsItem, RankedStory
from ..utils.logging import get_logger
from .score import calculate_composite_score

logger = get_logger("rank.select")


def rank_stories(
    items: list[NewsItem],
    weights: dict,
    time_window_hours: int,
    relevance_keywords: list[str]
) -> list[RankedStory]:
    """
    Rank news items by composite score.

    Args:
        items: List of news items
        weights: Ranking weight dict
        time_window_hours: Time window for recency calculation
        relevance_keywords: Keywords for relevance scoring

    Returns:
        List of RankedStory objects, sorted by score (descending)
    """
    logger.info(f"Ranking {len(items)} stories")

    ranked = []

    for item in items:
        scores = calculate_composite_score(
            item,
            weights,
            time_window_hours,
            relevance_keywords
        )

        ranked_story = RankedStory(
            news_item=item,
            score=scores["score"],
            recency_score=scores["recency_score"],
            credibility_score=scores["credibility_score"],
            engagement_score=scores["engagement_score"],
            uniqueness_score=scores["uniqueness_score"],
            relevance_score=scores["relevance_score"]
        )

        ranked.append(ranked_story)

    # Sort by score (descending)
    ranked.sort(key=lambda x: x.score, reverse=True)

    logger.info(
        f"Ranked stories - Top score: {ranked[0].score:.3f}, "
        f"Bottom score: {ranked[-1].score:.3f}"
    )

    return ranked


def select_top_stories(
    ranked_stories: list[RankedStory],
    top_count: int = 5,
    min_score: float = 0.3
) -> list[RankedStory]:
    """
    Select top N stories above minimum score threshold.

    Args:
        ranked_stories: List of ranked stories (sorted by score)
        top_count: Number of top stories to select
        min_score: Minimum score threshold

    Returns:
        List of top stories
    """
    # Filter by minimum score
    filtered = [story for story in ranked_stories if story.score >= min_score]

    # Select top N
    top_stories = filtered[:top_count]

    logger.info(
        f"Selected {len(top_stories)} top stories "
        f"(from {len(ranked_stories)} total, {len(filtered)} above threshold)"
    )

    return top_stories


def select_secondary_stories(
    ranked_stories: list[RankedStory],
    top_stories: list[RankedStory],
    secondary_count: int = 10,
    min_score: float = 0.2
) -> list[RankedStory]:
    """
    Select secondary stories for brief mentions.

    Args:
        ranked_stories: List of all ranked stories
        top_stories: List of top stories (to exclude)
        secondary_count: Number of secondary stories
        min_score: Minimum score threshold

    Returns:
        List of secondary stories
    """
    # Get IDs of top stories
    top_ids = {story.news_item.id for story in top_stories}

    # Filter out top stories and apply minimum score
    candidates = [
        story for story in ranked_stories
        if story.news_item.id not in top_ids and story.score >= min_score
    ]

    # Select secondary stories
    secondary = candidates[:secondary_count]

    logger.info(
        f"Selected {len(secondary)} secondary stories "
        f"(from {len(candidates)} candidates)"
    )

    return secondary


def filter_by_time_window(
    items: list[NewsItem],
    time_window_hours: int
) -> list[NewsItem]:
    """
    Filter news items by time window.

    Args:
        items: List of news items
        time_window_hours: Maximum age in hours

    Returns:
        Filtered list of news items
    """
    from datetime import datetime, timedelta

    cutoff = datetime.now() - timedelta(hours=time_window_hours)

    filtered = [item for item in items if item.published_at >= cutoff]

    logger.info(
        f"Filtered to {len(filtered)} items within {time_window_hours}h "
        f"(from {len(items)} total)"
    )

    return filtered
