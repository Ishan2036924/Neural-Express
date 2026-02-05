"""RSS feed ingestion module."""

import hashlib
from datetime import datetime
from typing import Optional
import feedparser
import httpx
from dateutil import parser as date_parser

from ..utils.schema import NewsItem
from ..utils.logging import get_logger

logger = get_logger("ingestion.rss")


async def fetch_rss_feed(
    feed_config: dict,
    timeout: int = 30
) -> list[NewsItem]:
    """
    Fetch and parse RSS feed.

    Args:
        feed_config: Feed configuration dict with name, url, credibility
        timeout: Request timeout in seconds

    Returns:
        List of normalized NewsItem objects
    """
    feed_name = feed_config["name"]
    feed_url = feed_config["url"]
    credibility = feed_config.get("credibility", 0.5)

    logger.info(f"Fetching RSS feed: {feed_name}")

    try:
        # Fetch feed content
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(feed_url)
            response.raise_for_status()
            content = response.text

        # Parse feed
        feed = feedparser.parse(content)

        if feed.bozo:
            logger.warning(f"Feed parsing error for {feed_name}: {feed.bozo_exception}")

        items = []
        for entry in feed.entries:
            try:
                news_item = _parse_feed_entry(entry, feed_name, credibility)
                if news_item:
                    items.append(news_item)
            except Exception as e:
                logger.warning(f"Error parsing entry from {feed_name}: {e}")
                continue

        logger.info(f"Fetched {len(items)} items from {feed_name}")
        return items

    except httpx.TimeoutException:
        logger.error(f"Timeout fetching {feed_name}")
        return []
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching {feed_name}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching {feed_name}: {e}")
        return []


def _parse_feed_entry(
    entry: feedparser.FeedParserDict,
    source_name: str,
    credibility: float
) -> Optional[NewsItem]:
    """
    Parse a single feed entry into NewsItem.

    Args:
        entry: Parsed feed entry
        source_name: Name of the source
        credibility: Source credibility score

    Returns:
        NewsItem or None if parsing fails
    """
    # Required fields
    if not hasattr(entry, "link") or not hasattr(entry, "title"):
        return None

    url = entry.link
    title = entry.title

    # Generate stable ID from URL
    item_id = hashlib.md5(url.encode()).hexdigest()

    # Parse published date
    published_at = _parse_date(entry)

    # Extract author
    author = getattr(entry, "author", None)

    # Extract summary
    summary_raw = ""
    if hasattr(entry, "summary"):
        summary_raw = entry.summary
    elif hasattr(entry, "description"):
        summary_raw = entry.description

    # Content snippet (first 500 chars of summary, stripped of HTML)
    content_snippet = _clean_html(summary_raw)[:500]

    # Extract tags
    tags = []
    if hasattr(entry, "tags"):
        tags = [tag.term for tag in entry.tags if hasattr(tag, "term")]

    # Create NewsItem
    news_item = NewsItem(
        id=item_id,
        source="rss",
        source_name=source_name,
        title=title,
        url=url,
        published_at=published_at,
        author=author,
        summary_raw=summary_raw,
        content_snippet=content_snippet,
        tags=tags,
        engagement={"credibility": credibility}
    )

    return news_item


def _parse_date(entry: feedparser.FeedParserDict) -> datetime:
    """Parse published date from feed entry."""
    # Try published_parsed first
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6])
        except Exception:
            pass

    # Try published string
    if hasattr(entry, "published"):
        try:
            return date_parser.parse(entry.published)
        except Exception:
            pass

    # Try updated_parsed
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        try:
            return datetime(*entry.updated_parsed[:6])
        except Exception:
            pass

    # Default to now
    return datetime.now()


def _clean_html(text: str) -> str:
    """Remove HTML tags from text."""
    import re

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()
