"""LLM prompt templates for summarization."""

STORY_SUMMARY_PROMPT = """You are an AI news editor creating concise, engaging summaries for a tech newsletter about artificial intelligence.

Given the following news article, create a structured summary suitable for a newsletter.

ARTICLE:
Title: {title}
Source: {source_name}
URL: {url}
Published: {published_at}
Content: {content}

INSTRUCTIONS:
1. Create a catchy, informative headline (under 70 characters)
2. Write a 1-2 line hook that grabs attention
3. Provide 3-6 key detail bullets
4. Explain why this matters in 2-4 lines
5. Categorize the story (Chips|Research|Policy|Tools|Business|Funding)
6. Suggest image keywords and credit line

Respond in JSON format:
{{
  "headline": "string",
  "hook": "string",
  "details": ["string", "string", ...],
  "why_it_matters": "string",
  "category": "string",
  "image_suggestion": {{
    "search_keywords": ["string", ...],
    "credit_line": "string",
    "source_url": null,
    "fallback_banner": false
  }}
}}

Focus on accuracy, clarity, and reader engagement. Maintain a professional but accessible tone."""


NEWSLETTER_INTRO_PROMPT = """You are an AI news editor writing the introduction for today's AI newsletter.

Here are the top {count} stories we're covering:
{story_summaries}

Write a brief, engaging introduction (2-3 sentences) that:
1. Greets the reader warmly
2. Previews the key themes or highlights
3. Sets an informative but conversational tone

Keep it under 50 words. Start with "Good morning, Reader 👋"
"""


def get_story_summary_prompt(
    title: str,
    source_name: str,
    url: str,
    published_at: str,
    content: str
) -> str:
    """
    Generate story summarization prompt.

    Args:
        title: Article title
        source_name: Source name
        url: Article URL
        published_at: Publication date
        content: Article content

    Returns:
        Formatted prompt string
    """
    return STORY_SUMMARY_PROMPT.format(
        title=title,
        source_name=source_name,
        url=url,
        published_at=published_at,
        content=content[:2000]  # Limit content length
    )


def get_newsletter_intro_prompt(
    story_summaries: list[str]
) -> str:
    """
    Generate newsletter introduction prompt.

    Args:
        story_summaries: List of brief story summaries

    Returns:
        Formatted prompt string
    """
    summaries_text = "\n".join(
        f"{i+1}. {summary}"
        for i, summary in enumerate(story_summaries)
    )

    return NEWSLETTER_INTRO_PROMPT.format(
        count=len(story_summaries),
        story_summaries=summaries_text
    )
