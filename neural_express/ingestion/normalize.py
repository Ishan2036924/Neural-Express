"""Normalization utilities for ingested data."""

from ..utils.schema import NewsItem
from ..utils.logging import get_logger

logger = get_logger("ingestion.normalize")


def normalize_items(items: list[NewsItem]) -> list[NewsItem]:
    """
    Normalize and clean news items.

    Args:
        items: List of news items

    Returns:
        List of normalized news items
    """
    normalized = []

    for item in items:
        # Basic validation
        if not item.title or not item.url:
            logger.warning(f"Skipping item with missing title or URL: {item.id}")
            continue

        # Clean title
        item.title = _clean_text(item.title)

        # Clean summary
        item.summary_raw = _clean_text(item.summary_raw)
        item.content_snippet = _clean_text(item.content_snippet)

        # Normalize tags
        item.tags = [tag.lower().strip() for tag in item.tags]

        normalized.append(item)

    logger.info(f"Normalized {len(normalized)} items from {len(items)} raw items")
    return normalized


def _clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""

    # Remove excessive whitespace
    text = " ".join(text.split())

    # Remove common artifacts
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = text.replace("\r", " ")

    return text.strip()
