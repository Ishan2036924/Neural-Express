"""Tests for data schemas."""

import pytest
from datetime import datetime
from neural_express.utils.schema import NewsItem, StorySummary, ImageSuggestion, RankedStory


def test_news_item_creation():
    """Test NewsItem creation."""
    item = NewsItem(
        id="test123",
        source="rss",
        source_name="Test Source",
        title="Test Article",
        url="https://example.com/article",
        published_at=datetime.now(),
        author="Test Author",
        summary_raw="Test summary",
        content_snippet="Test content",
        tags=["ai", "ml"],
        engagement={"credibility": 0.9}
    )

    assert item.id == "test123"
    assert item.source == "rss"
    assert len(item.tags) == 2
    assert item.engagement["credibility"] == 0.9
    assert len(item.duplicates) == 0


def test_image_suggestion():
    """Test ImageSuggestion creation."""
    suggestion = ImageSuggestion(
        search_keywords=["ai", "robot", "tech"],
        credit_line="Image source: OpenAI",
        source_url="https://example.com/image.jpg",
        fallback_banner=False
    )

    assert len(suggestion.search_keywords) == 3
    assert "OpenAI" in suggestion.credit_line
    assert suggestion.fallback_banner is False


def test_story_summary():
    """Test StorySummary creation."""
    image = ImageSuggestion(
        search_keywords=["test"],
        credit_line="Test Credit"
    )

    summary = StorySummary(
        headline="Test Headline",
        hook="Test hook line",
        details=["Detail 1", "Detail 2", "Detail 3"],
        why_it_matters="This is important because...",
        category="Research",
        image_suggestion=image
    )

    assert summary.headline == "Test Headline"
    assert len(summary.details) == 3
    assert summary.category == "Research"


def test_ranked_story():
    """Test RankedStory creation."""
    item = NewsItem(
        id="test123",
        source="rss",
        source_name="Test",
        title="Test",
        url="https://example.com",
        published_at=datetime.now(),
        author=None,
        summary_raw="",
        content_snippet=""
    )

    ranked = RankedStory(
        news_item=item,
        score=0.85,
        recency_score=0.9,
        credibility_score=0.95,
        engagement_score=0.7,
        uniqueness_score=0.8,
        relevance_score=0.9
    )

    assert ranked.score == 0.85
    assert ranked.news_item.id == "test123"
    assert ranked.summary is None
