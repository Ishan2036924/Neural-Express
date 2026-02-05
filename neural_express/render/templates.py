"""Markdown templates for newsletter generation."""

from datetime import datetime


NEWSLETTER_HEADER = """# NEURAL EXPRESS

*Your {mode} briefing on the AI stories that matter*

{intro}

In today's NEURAL EXPRESS:
{toc}

---
"""


MAIN_STORY_TEMPLATE = """## {category_emoji} {headline}

*{image_credit}*

{hook}

**The details:**
{details}

**Why it matters:** {why_it_matters}

[Read more]({url})

---
"""


SECONDARY_STORIES_SECTION = """## Everything else in AI today

{stories}

---
"""


SECONDARY_STORY_ITEM = """- **{headline}** — {snippet} [({source})]({url})"""


NEWSLETTER_FOOTER = """---

### Sources

{sources}

---

**That's all for {date}!**

Stay curious,
The NEURAL EXPRESS Team

---

*Crafted with [Claude Code](https://claude.com/claude-code)*
"""


CATEGORY_EMOJIS = {
    "Chips": "💻",
    "Research": "🔬",
    "Policy": "⚖️",
    "Tools": "🛠️",
    "Business": "📢",
    "Funding": "💰"
}


def get_category_emoji(category: str) -> str:
    """Get emoji for story category."""
    return CATEGORY_EMOJIS.get(category, "📰")


def format_toc_item(headline: str) -> str:
    """Format table of contents item."""
    return f"- {headline}"


def format_source_list(sources: list[tuple[str, str]]) -> str:
    """
    Format source list.

    Args:
        sources: List of (name, url) tuples

    Returns:
        Formatted markdown list
    """
    items = [f"- [{name}]({url})" for name, url in sources]
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
