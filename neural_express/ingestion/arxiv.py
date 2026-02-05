"""arXiv API ingestion module (optional)."""

import hashlib
from datetime import datetime
from typing import Optional
import httpx
import xml.etree.ElementTree as ET

from ..utils.schema import NewsItem
from ..utils.logging import get_logger

logger = get_logger("ingestion.arxiv")

ARXIV_API_URL = "http://export.arxiv.org/api/query"


async def fetch_arxiv_papers(
    query: str = "cat:cs.AI OR cat:cs.LG OR cat:cs.CL",
    max_results: int = 50,
    timeout: int = 30
) -> list[NewsItem]:
    """
    Fetch recent papers from arXiv.

    Args:
        query: arXiv API query string
        max_results: Maximum number of results
        timeout: Request timeout in seconds

    Returns:
        List of normalized NewsItem objects
    """
    logger.info(f"Fetching arXiv papers: {query}")

    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(ARXIV_API_URL, params=params)
            response.raise_for_status()
            content = response.text

        # Parse XML
        root = ET.fromstring(content)
        namespace = {"atom": "http://www.w3.org/2005/Atom"}

        items = []
        for entry in root.findall("atom:entry", namespace):
            try:
                news_item = _parse_arxiv_entry(entry, namespace)
                if news_item:
                    items.append(news_item)
            except Exception as e:
                logger.warning(f"Error parsing arXiv entry: {e}")
                continue

        logger.info(f"Fetched {len(items)} papers from arXiv")
        return items

    except httpx.TimeoutException:
        logger.error("Timeout fetching arXiv")
        return []
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching arXiv: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching arXiv: {e}")
        return []


def _parse_arxiv_entry(
    entry: ET.Element,
    namespace: dict
) -> Optional[NewsItem]:
    """
    Parse arXiv entry into NewsItem.

    Args:
        entry: XML entry element
        namespace: XML namespace dict

    Returns:
        NewsItem or None if parsing fails
    """
    # Extract fields
    title_elem = entry.find("atom:title", namespace)
    id_elem = entry.find("atom:id", namespace)
    summary_elem = entry.find("atom:summary", namespace)
    published_elem = entry.find("atom:published", namespace)
    author_elems = entry.findall("atom:author", namespace)

    if title_elem is None or id_elem is None:
        return None

    title = title_elem.text.strip()
    url = id_elem.text.strip()

    # Generate stable ID
    item_id = hashlib.md5(url.encode()).hexdigest()

    # Parse date
    published_at = datetime.now()
    if published_elem is not None:
        try:
            published_at = datetime.fromisoformat(
                published_elem.text.replace("Z", "+00:00")
            )
        except Exception:
            pass

    # Authors
    authors = []
    for author_elem in author_elems:
        name_elem = author_elem.find("atom:name", namespace)
        if name_elem is not None:
            authors.append(name_elem.text.strip())

    author = ", ".join(authors) if authors else None

    # Summary
    summary_raw = summary_elem.text.strip() if summary_elem is not None else ""
    content_snippet = summary_raw[:500]

    # Extract categories
    tags = []
    for category_elem in entry.findall("atom:category", namespace):
        term = category_elem.get("term")
        if term:
            tags.append(term)

    # Create NewsItem
    news_item = NewsItem(
        id=item_id,
        source="arxiv",
        source_name="arXiv",
        title=title,
        url=url,
        published_at=published_at,
        author=author,
        summary_raw=summary_raw,
        content_snippet=content_snippet,
        tags=tags,
        engagement={"credibility": 0.95}  # arXiv papers are high credibility
    )

    return news_item
