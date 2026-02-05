"""Tests for ranking logic."""

import pytest
from datetime import datetime, timedelta
from neural_express.utils.schema import NewsItem
from neural_express.rank.score import (
    calculate_recency_score,
    calculate_credibility_score,
    calculate_uniqueness_score,
    calculate_relevance_score,
    calculate_composite_score
)


def test_recency_score_recent():
    """Test recency score for recent item."""
    item = NewsItem(
        id="1",
        source="rss",
        source_name="Test",
        title="Test",
        url="https://example.com",
        published_at=datetime.now() - timedelta(hours=12),  # 12 hours ago
        author=None,
        summary_raw="",
        content_snippet=""
    )

    score = calculate_recency_score(item, time_window_hours=24)
    assert score == 1.0  # Within window


def test_recency_score_old():
    """Test recency score for old item."""
    item = NewsItem(
        id="1",
        source="rss",
        source_name="Test",
        title="Test",
        url="https://example.com",
        published_at=datetime.now() - timedelta(hours=72),  # 3 days ago
        author=None,
        summary_raw="",
        content_snippet=""
    )

    score = calculate_recency_score(item, time_window_hours=24)
    assert score < 1.0  # Outside window


def test_credibility_score():
    """Test credibility score."""
    item = NewsItem(
        id="1",
        source="rss",
        source_name="Test",
        title="Test",
        url="https://example.com",
        published_at=datetime.now(),
        author=None,
        summary_raw="",
        content_snippet="",
        engagement={"credibility": 0.85}
    )

    score = calculate_credibility_score(item)
    assert score == 0.85


def test_uniqueness_score():
    """Test uniqueness score."""
    # Unique item
    item1 = NewsItem(
        id="1",
        source="rss",
        source_name="Test",
        title="Test",
        url="https://example.com",
        published_at=datetime.now(),
        author=None,
        summary_raw="",
        content_snippet="",
        duplicates=[]
    )

    score1 = calculate_uniqueness_score(item1)
    assert score1 == 1.0

    # Item with duplicates
    item2 = NewsItem(
        id="2",
        source="rss",
        source_name="Test",
        title="Test",
        url="https://example.com",
        published_at=datetime.now(),
        author=None,
        summary_raw="",
        content_snippet="",
        duplicates=["url1", "url2", "url3"]
    )

    score2 = calculate_uniqueness_score(item2)
    assert score2 == 0.25  # 1 / (1 + 3 duplicates)


def test_relevance_score():
    """Test relevance score."""
    item = NewsItem(
        id="1",
        source="rss",
        source_name="Test",
        title="New LLM uses transformer architecture for AI",
        url="https://example.com",
        published_at=datetime.now(),
        author=None,
        summary_raw="",
        content_snippet="Deep learning and neural networks power this model"
    )

    keywords = ["llm", "transformer", "ai", "neural network", "deep learning"]
    score = calculate_relevance_score(item, keywords)

    assert score > 0.5  # Should have high relevance


def test_composite_score():
    """Test composite score calculation."""
    item = NewsItem(
        id="1",
        source="rss",
        source_name="Test",
        title="AI breakthrough",
        url="https://example.com",
        published_at=datetime.now(),
        author=None,
        summary_raw="",
        content_snippet="New AI technology",
        engagement={"credibility": 0.9}
    )

    weights = {
        "recency": 0.3,
        "credibility": 0.25,
        "engagement": 0.15,
        "uniqueness": 0.15,
        "relevance": 0.15
    }

    scores = calculate_composite_score(
        item,
        weights,
        time_window_hours=24,
        relevance_keywords=["ai"]
    )

    assert "score" in scores
    assert 0 <= scores["score"] <= 1
    assert all(k in scores for k in [
        "recency_score",
        "credibility_score",
        "engagement_score",
        "uniqueness_score",
        "relevance_score"
    ])
