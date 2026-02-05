"""Tests for rendering logic."""

import pytest
from datetime import datetime
from neural_express.utils.schema import NewsItem, RankedStory, StorySummary, ImageSuggestion
from neural_express.render.beehiiv_md import render_newsletter
from neural_express.render.templates import (
    get_category_emoji,
    format_details_list,
    format_source_list
)


def test_category_emoji():
    """Test category emoji mapping."""
    assert get_category_emoji("Chips") == "💻"
    assert get_category_emoji("Research") == "🔬"
    assert get_category_emoji("Policy") == "⚖️"
    assert get_category_emoji("Unknown") == "📰"


def test_format_details_list():
    """Test details list formatting."""
    details = ["Detail 1", "Detail 2", "Detail 3"]
    formatted = format_details_list(details)

    assert "- Detail 1" in formatted
    assert "- Detail 2" in formatted
    assert "- Detail 3" in formatted


def test_format_source_list():
    """Test source list formatting."""
    sources = [
        ("TechCrunch", "https://techcrunch.com/article1"),
        ("MIT Review", "https://mit.edu/article2")
    ]

    formatted = format_source_list(sources)

    assert "[TechCrunch]" in formatted
    assert "(https://techcrunch.com/article1)" in formatted


def test_render_newsletter():
    """Test complete newsletter rendering."""
    # Create sample story
    item = NewsItem(
        id="1",
        source="rss",
        source_name="TechCrunch",
        title="AI Breakthrough",
        url="https://example.com/article",
        published_at=datetime.now(),
        author="Test Author",
        summary_raw="Summary",
        content_snippet="Content snippet"
    )

    image = ImageSuggestion(
        search_keywords=["ai", "tech"],
        credit_line="Image source: TechCrunch"
    )

    summary = StorySummary(
        headline="Major AI Breakthrough Announced",
        hook="A new AI model achieves unprecedented performance.",
        details=["Detail 1", "Detail 2", "Detail 3"],
        why_it_matters="This represents a significant advance in AI capabilities.",
        category="Research",
        image_suggestion=image
    )

    story = RankedStory(
        news_item=item,
        score=0.9,
        recency_score=1.0,
        credibility_score=0.85,
        engagement_score=0.5,
        uniqueness_score=1.0,
        relevance_score=0.9,
        summary=summary
    )

    # Render newsletter
    newsletter = render_newsletter(
        top_stories=[story],
        secondary_stories=[],
        intro="Good morning, Reader 👋\n\nToday's top AI stories.",
        mode="daily"
    )

    # Verify content
    assert "NEURAL EXPRESS" in newsletter
    assert "Major AI Breakthrough Announced" in newsletter
    assert "A new AI model achieves unprecedented performance" in newsletter
    assert "Detail 1" in newsletter
    assert "https://example.com/article" in newsletter
    assert "TechCrunch" in newsletter
