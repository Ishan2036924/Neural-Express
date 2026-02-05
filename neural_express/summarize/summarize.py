"""Story summarization pipeline."""

from typing import Optional
from ..utils.schema import RankedStory, StorySummary, ImageSuggestion
from ..utils.logging import get_logger
from .llm import LLMClient
from .prompts import get_story_summary_prompt

logger = get_logger("summarize")


def summarize_story(
    story: RankedStory,
    llm_client: LLMClient
) -> Optional[StorySummary]:
    """
    Generate summary for a news story using LLM.

    Args:
        story: Ranked story to summarize
        llm_client: LLM client

    Returns:
        StorySummary or None if generation fails
    """
    item = story.news_item

    logger.info(f"Summarizing story: {item.title[:50]}...")

    try:
        # Generate prompt
        prompt = get_story_summary_prompt(
            title=item.title,
            source_name=item.source_name,
            url=item.url,
            published_at=item.published_at.isoformat(),
            content=item.content_snippet
        )

        # Call LLM
        response = llm_client.generate_json(prompt)

        # Parse response
        summary = _parse_summary_response(response)

        logger.info(f"Generated summary with {len(summary.details)} details")

        return summary

    except Exception as e:
        logger.error(f"Failed to summarize story: {e}")
        return None


def _parse_summary_response(response: dict) -> StorySummary:
    """
    Parse LLM response into StorySummary.

    Args:
        response: JSON response from LLM

    Returns:
        StorySummary object
    """
    # Parse image suggestion
    image_data = response.get("image_suggestion", {})
    image_suggestion = ImageSuggestion(
        search_keywords=image_data.get("search_keywords", []),
        credit_line=image_data.get("credit_line", ""),
        source_url=image_data.get("source_url"),
        fallback_banner=image_data.get("fallback_banner", False)
    )

    # Create summary
    summary = StorySummary(
        headline=response.get("headline", ""),
        hook=response.get("hook", ""),
        details=response.get("details", []),
        why_it_matters=response.get("why_it_matters", ""),
        category=response.get("category", "Business"),
        image_suggestion=image_suggestion
    )

    return summary


async def summarize_stories(
    stories: list[RankedStory],
    llm_client: LLMClient
) -> list[RankedStory]:
    """
    Summarize multiple stories (can be parallelized).

    Args:
        stories: List of ranked stories
        llm_client: LLM client

    Returns:
        List of ranked stories with summaries attached
    """
    logger.info(f"Summarizing {len(stories)} stories")

    summarized = []

    for story in stories:
        summary = summarize_story(story, llm_client)

        if summary:
            story.summary = summary
            summarized.append(story)
        else:
            logger.warning(f"Skipping story without summary: {story.news_item.title[:50]}")

    logger.info(f"Successfully summarized {len(summarized)} stories")

    return summarized


def generate_newsletter_intro(
    stories: list[RankedStory],
    llm_client: LLMClient
) -> str:
    """
    Generate newsletter introduction.

    Args:
        stories: List of top stories
        llm_client: LLM client

    Returns:
        Introduction text
    """
    from .prompts import get_newsletter_intro_prompt

    logger.info("Generating newsletter introduction")

    # Create brief summaries
    story_summaries = [
        story.summary.headline if story.summary else story.news_item.title
        for story in stories
    ]

    try:
        prompt = get_newsletter_intro_prompt(story_summaries)
        intro = llm_client.generate(prompt)

        logger.info("Generated newsletter introduction")

        return intro.strip()

    except Exception as e:
        logger.error(f"Failed to generate introduction: {e}")
        # Fallback
        return "Good morning, Reader 👋\n\nHere are today's top AI stories."
