"""Beehiiv-compatible markdown newsletter renderer."""

from datetime import datetime
from typing import Optional
from ..utils.schema import RankedStory
from ..utils.logging import get_logger
from .templates import (
    NEWSLETTER_HEADER,
    IN_THIS_ISSUE_SECTION,
    MAIN_STORY_TEMPLATE,
    QUICK_BITES_SECTION,
    QUICK_BITE_ITEM,
    DEVELOPING_STORIES_SECTION,
    DEVELOPING_STORY_CHAIN,
    DEVELOPING_STORY_TIMELINE_ENTRY,
    JOBS_SECTION,
    JOB_ITEM,
    TOOLS_SECTION,
    TOOL_ITEM,
    SOURCES_SECTION,
    NEWSLETTER_FOOTER,
    PLACEHOLDER_JOBS,
    PLACEHOLDER_TOOLS,
    get_category_emoji,
    get_date_range,
    format_toc_item,
    format_source_list,
    format_details_list
)

logger = get_logger("render")


def render_newsletter(
    top_stories: list[RankedStory],
    secondary_stories: list[RankedStory],
    intro: str,
    mode: str = "daily",
    story_chains: Optional[dict] = None
) -> str:
    """
    Render complete newsletter with all 9 sections.

    Args:
        top_stories: List of main stories with summaries
        secondary_stories: List of secondary stories
        intro: Newsletter introduction text
        mode: "daily" or "weekly"
        story_chains: Optional dict of story chains (chain_id -> list of stories)

    Returns:
        Complete newsletter markdown
    """
    logger.info(
        f"Rendering newsletter with {len(top_stories)} main stories "
        f"and {len(secondary_stories)} secondary stories"
    )

    sections = []

    # Section 1: HEADER
    header = _render_header(intro, mode)
    sections.append(header)

    # Section 2: IN THIS ISSUE
    in_this_issue = _render_in_this_issue(top_stories)
    sections.append(in_this_issue)

    # Section 3: TOP STORIES
    sections.append("## TOP STORIES\n")
    for i, story in enumerate(top_stories, 1):
        story_section = _render_main_story(story, i)
        if story_section:
            sections.append(story_section)

    # Section 4: QUICK BITES
    if secondary_stories:
        quick_bites = _render_quick_bites(secondary_stories)
        sections.append(quick_bites)

    # Section 5: DEVELOPING STORIES
    if mode == "weekly" and story_chains:
        developing = _render_developing_stories(story_chains)
        sections.append(developing)

    # Section 6: TOP AI JOBS
    jobs = _render_jobs()
    sections.append(jobs)

    # Section 7: TRENDING AI TOOLS
    tools = _render_tools()
    sections.append(tools)

    # Section 8: SOURCES
    all_stories = top_stories + secondary_stories
    sources = _render_sources(all_stories)
    sections.append(sources)

    # Section 9: FOOTER
    footer = _render_footer()
    sections.append(footer)

    # Combine
    newsletter = "\n".join(sections)

    logger.info(f"Rendered newsletter ({len(newsletter)} characters)")

    return newsletter


def _render_header(intro: str, mode: str) -> str:
    """Render newsletter header with date range and greeting."""
    date_range = get_date_range(mode)

    return NEWSLETTER_HEADER.format(
        date_range=date_range,
        wave="\U0001f44b",
        intro=intro
    )


def _render_in_this_issue(stories: list[RankedStory]) -> str:
    """Render IN THIS ISSUE numbered headlines."""
    toc_items = []
    for i, story in enumerate(stories, 1):
        if story.summary:
            headline = story.summary.headline
            category = story.summary.category
        else:
            headline = story.news_item.title
            category = "News"

        toc_items.append(format_toc_item(headline, i, category))

    numbered_headlines = "\n".join(toc_items)

    return IN_THIS_ISSUE_SECTION.format(numbered_headlines=numbered_headlines)


def _render_main_story(story: RankedStory, story_number: int) -> str:
    """Render a main story with full details."""
    item = story.news_item
    summary = story.summary

    if not summary:
        logger.warning(f"Story missing summary: {item.title[:50]}")
        return ""

    category_emoji = get_category_emoji(summary.category)
    details = format_details_list(summary.details)

    return MAIN_STORY_TEMPLATE.format(
        story_number=story_number,
        category_emoji=category_emoji,
        headline=summary.headline,
        category=summary.category,
        source=item.source_name,
        hook=summary.hook,
        details=details,
        why_it_matters=summary.why_it_matters,
        url=item.url
    )


def _render_quick_bites(stories: list[RankedStory]) -> str:
    """Render quick bites section."""
    story_items = []

    for story in stories:
        item = story.news_item

        if story.summary:
            headline = story.summary.headline
            snippet = story.summary.hook[:150]
        else:
            headline = item.title
            snippet = item.content_snippet[:150]

        story_item = QUICK_BITE_ITEM.format(
            headline=headline,
            snippet=snippet,
            source=item.source_name,
            url=item.url
        )

        story_items.append(story_item)

    stories_text = "\n".join(story_items)

    return QUICK_BITES_SECTION.format(stories=stories_text)


def _render_developing_stories(story_chains: dict) -> str:
    """Render developing stories with timelines."""
    chain_sections = []

    for chain_id, stories in story_chains.items():
        if len(stories) < 2:
            continue

        # Sort by date
        sorted_stories = sorted(stories, key=lambda s: s.news_item.published_at)

        # Chain title from first story
        first = sorted_stories[0]
        chain_title = first.summary.headline if first.summary else first.news_item.title

        # Build timeline
        timeline_entries = []
        for story in sorted_stories:
            date_str = story.news_item.published_at.strftime("%b %d")
            headline = story.summary.headline if story.summary else story.news_item.title
            source = story.news_item.source_name

            entry = DEVELOPING_STORY_TIMELINE_ENTRY.format(
                date=date_str,
                headline=headline,
                source=source
            )
            timeline_entries.append(entry)

        timeline = "\n".join(timeline_entries)

        # Significance from the latest story
        latest = sorted_stories[-1]
        significance = (
            latest.summary.why_it_matters if latest.summary
            else f"This developing story from {latest.news_item.source_name} continues to evolve."
        )

        chain_section = DEVELOPING_STORY_CHAIN.format(
            chain_title=chain_title,
            timeline=timeline,
            significance=significance
        )
        chain_sections.append(chain_section)

    if not chain_sections:
        return ""

    chains_text = "\n\n".join(chain_sections)

    return DEVELOPING_STORIES_SECTION.format(chains=chains_text)


def _render_jobs() -> str:
    """Render top AI jobs section."""
    job_items = []
    for title, company, location, description in PLACEHOLDER_JOBS:
        job_items.append(JOB_ITEM.format(
            title=title,
            company=company,
            location=location,
            description=description
        ))

    jobs_text = "\n".join(job_items)
    return JOBS_SECTION.format(jobs=jobs_text)


def _render_tools() -> str:
    """Render trending AI tools section."""
    tool_items = []
    for name, description, url in PLACEHOLDER_TOOLS:
        tool_items.append(TOOL_ITEM.format(
            name=name,
            description=description,
            url=url
        ))

    tools_text = "\n".join(tool_items)
    return TOOLS_SECTION.format(tools=tools_text)


def _render_sources(stories: list[RankedStory]) -> str:
    """Render sources section."""
    sources = []
    seen_urls = set()

    for story in stories:
        item = story.news_item
        if item.url not in seen_urls:
            sources.append((item.source_name, item.url))
            seen_urls.add(item.url)

    sources_text = format_source_list(sources)

    return SOURCES_SECTION.format(sources=sources_text)


def _render_footer() -> str:
    """Render newsletter footer."""
    return NEWSLETTER_FOOTER.format(
        wave="\U0001f44b",
        copyright="\u00a9"
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
