"""Markdown templates for newsletter generation."""

from datetime import datetime, timedelta


NEWSLETTER_HEADER = """# NEURAL EXPRESS WEEKLY

*{date_range}*

*Your AI news briefing curated by intelligent agents*

Good morning, Reader {wave}

{intro}

---
"""


IN_THIS_ISSUE_SECTION = """## IN THIS ISSUE

{numbered_headlines}

---
"""


MAIN_STORY_TEMPLATE = """### {story_number}. {category_emoji} {headline}

*{category} | {source}*

{hook}

**The details:**
{details}

**Why it matters:** {why_it_matters}

[Read more]({url})

---
"""


QUICK_BITES_SECTION = """## QUICK BITES

{stories}

---
"""


QUICK_BITE_ITEM = """- **{headline}** — {snippet} [({source})]({url})"""


DEVELOPING_STORIES_SECTION = """## DEVELOPING STORIES

*Stories that evolved over the week*

{chains}

---
"""


DEVELOPING_STORY_CHAIN = """**{chain_title}**

{timeline}

*What it means:* {significance}
"""


DEVELOPING_STORY_TIMELINE_ENTRY = """- **{date}:** {headline} *({source})*"""


JOBS_SECTION = """## TOP AI JOBS THIS WEEK

{jobs}

---
"""


JOB_ITEM = """- **{title}** at {company} — {location} — {description}"""


TOOLS_SECTION = """## TRENDING AI TOOLS

{tools}

---
"""


TOOL_ITEM = """- **{name}** — {description} [Link]({url})"""


SOURCES_SECTION = """## SOURCES

{sources}

---
"""


NEWSLETTER_FOOTER = """---

Thanks for reading Neural Express! {wave}

*Reply to this email with feedback or questions.*

*{copyright} 2026 Neural Express. All rights reserved.*

*Crafted with [Claude Code](https://claude.com/claude-code)*
"""


CATEGORY_EMOJIS = {
    "Chips": "\U0001f4bb",
    "Hardware": "\U0001f4bb",
    "Research": "\U0001f52c",
    "Policy": "\u2696\ufe0f",
    "Tools": "\U0001f527",
    "Business": "\U0001f4e2",
    "Funding": "\U0001f4b0",
    "Robotics": "\U0001f916",
    "AGI/Safety": "\U0001f9e0",
    "Creative AI": "\U0001f3a8",
}


def get_category_emoji(category: str) -> str:
    """Get emoji for story category."""
    return CATEGORY_EMOJIS.get(category, "\U0001f4f0")


def get_date_range(mode: str = "weekly") -> str:
    """Get formatted date range string."""
    end_date = datetime.now()
    if mode == "weekly":
        start_date = end_date - timedelta(days=10)
        return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    else:
        return end_date.strftime("%B %d, %Y")


def format_toc_item(headline: str, number: int, category: str) -> str:
    """Format table of contents item with number and category."""
    emoji = get_category_emoji(category)
    return f"{number}. {emoji} {headline} [{category}]"


def format_source_list(sources: list[tuple[str, str]]) -> str:
    """
    Format source list as numbered items.

    Args:
        sources: List of (name, url) tuples

    Returns:
        Formatted markdown list
    """
    items = [f"{i}. [{name}]({url})" for i, (name, url) in enumerate(sources, 1)]
    return "\n".join(items)


def format_details_list(details: list[str]) -> str:
    """
    Format details as bullet list.

    Args:
        details: List of detail strings

    Returns:
        Formatted markdown list
    """
    items = [f"- {detail}" for detail in details]
    return "\n".join(items)


# Placeholder data for jobs and tools sections
PLACEHOLDER_JOBS = [
    ("Senior ML Engineer", "OpenAI", "San Francisco, CA", "Build next-gen language models"),
    ("AI Research Scientist", "Google DeepMind", "London, UK", "Advance AGI research"),
    ("Applied AI Lead", "Anthropic", "Remote", "Lead safety research initiatives"),
    ("Computer Vision Engineer", "Tesla", "Palo Alto, CA", "Autonomous driving AI"),
    ("NLP Engineer", "Meta", "Menlo Park, CA", "Large-scale NLP systems"),
]

PLACEHOLDER_TOOLS = [
    ("Claude Code", "AI-powered coding assistant for the terminal", "https://claude.com/claude-code"),
    ("Midjourney v6", "State-of-the-art text-to-image generation", "https://midjourney.com"),
    ("LangChain", "Framework for building LLM applications", "https://langchain.com"),
    ("Replicate", "Run and deploy ML models via API", "https://replicate.com"),
    ("Weights & Biases", "ML experiment tracking and visualization", "https://wandb.ai"),
]
