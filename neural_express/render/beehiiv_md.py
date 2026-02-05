"""Beehiiv-compatible markdown newsletter renderer."""

from datetime import datetime
from ..utils.schema import RankedStory
from ..utils.logging import get_logger
from .templates import (
    NEWSLETTER_HEADER,
    MAIN_STORY_TEMPLATE,
    SECONDARY_STORIES_SECTION,
    SECONDARY_STORY_ITEM,
    NEWSLETTER_FOOTER,
    get_category_emoji,
    format_toc_item,
    format_source_list,
    format_details_list
)

logger = get_logger("render")


def render_newsletter(
    top_stories: list[RankedStory],
    secondary_stories: list[RankedStory],
    intro: str,
    mode: str = "daily"
) -> str:
    """
    Render complete newsletter in Beehiiv-compatible markdown.

    Args:
        top_stories: List of main stories with summaries
        secondary_stories: List of secondary stories
        intro: Newsletter introduction text
        mode: "daily" or "weekly"

    Returns:
        Complete newsletter markdown
    """
    logger.info(
        f"Rendering newsletter with {len(top_stories)} main stories "
        f"and {len(secondary_stories)} secondary stories"
    )

    sections = []

    # Header
    header = _render_header(top_stories, intro, mode)
    sections.append(header)

    # Main stories
    sections.append("## LATEST DEVELOPMENTS\n")

    for story in top_stories:
        story_section = _render_main_story(story)
        sections.append(story_section)

    # Secondary stories
    if secondary_stories:
        secondary_section = _render_secondary_stories(secondary_stories)
        sections.append(secondary_section)

    # Footer
    all_stories = top_stories + secondary_stories
    footer = _render_footer(all_stories, mode)
    sections.append(footer)

    # Combine
    newsletter = "\n".join(sections)

    logger.info(f"Rendered newsletter ({len(newsletter)} characters)")

    return newsletter


def _render_header(
    stories: list[RankedStory],
    intro: str,
    mode: str
) -> str:
    """Render newsletter header."""
    # Table of contents
    toc_items = []
    for story in stories:
        if story.summary:
            headline = story.summary.headline
        else:
            headline = story.news_item.title

        toc_items.append(format_toc_item(headline))

    toc = "\n".join(toc_items)

    return NEWSLETTER_HEADER.format(
        mode=mode,
        intro=intro,
        toc=toc
    )


def _render_main_story(story: RankedStory) -> str:
    """Render a main story with full details."""
    item = story.news_item
    summary = story.summary

    if not summary:
        logger.warning(f"Story missing summary: {item.title[:50]}")
        return ""

    # Get category emoji
    category_emoji = get_category_emoji(summary.category)

    # Format details
    details = format_details_list(summary.details)

    # Image credit
    image_credit = summary.image_suggestion.credit_line

    return MAIN_STORY_TEMPLATE.format(
        category_emoji=category_emoji,
        headline=summary.headline,
        image_credit=image_credit,
        hook=summary.hook,
        details=details,
        why_it_matters=summary.why_it_matters,
        url=item.url
    )


def _render_secondary_stories(stories: list[RankedStory]) -> str:
    """Render secondary stories section."""
    story_items = []

    for story in stories:
        item = story.news_item

        # Use summary headline if available, otherwise original title
        if story.summary:
            headline = story.summary.headline
            snippet = story.summary.hook
        else:
            headline = item.title
            snippet = item.content_snippet[:150]

        story_item = SECONDARY_STORY_ITEM.format(
            headline=headline,
            snippet=snippet,
            source=item.source_name,
            url=item.url
        )

        story_items.append(story_item)

    stories_text = "\n".join(story_items)

    return SECONDARY_STORIES_SECTION.format(stories=stories_text)


def _render_footer(stories: list[RankedStory], mode: str) -> str:
    """Render newsletter footer with sources."""
    # Collect sources
    sources = []
    seen_urls = set()

    for story in stories:
        item = story.news_item

        if item.url not in seen_urls:
            sources.append((item.source_name, item.url))
            seen_urls.add(item.url)

    sources_text = format_source_list(sources)

    # Current date
    date = datetime.now().strftime("%B %d, %Y")

    return NEWSLETTER_FOOTER.format(
        sources=sources_text,
        date=date
    )


def save_newsletter(
    newsletter: str,
    filepath: str
) -> None:
    """
    Save newsletter to file.

    Args:
        newsletter: Newsletter markdown content
        filepath: Output file path
    """
    from pathlib import Path
    from ..utils.io import save_markdown

    save_markdown(newsletter, Path(filepath))

    logger.info(f"Saved newsletter to {filepath}")
