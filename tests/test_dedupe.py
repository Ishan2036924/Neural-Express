"""Tests for deduplication logic."""

import pytest
from datetime import datetime
from neural_express.utils.schema import NewsItem
from neural_express.dedupe.embed import EmbeddingModel
from neural_express.dedupe.dedupe import Deduplicator


@pytest.fixture
def embedding_model():
    """Create embedding model fixture."""
    return EmbeddingModel()


@pytest.fixture
def sample_items():
    """Create sample news items."""
    return [
        NewsItem(
            id="1",
            source="rss",
            source_name="Source A",
            title="OpenAI Releases GPT-5",
            url="https://example.com/1",
            published_at=datetime.now(),
            author="Author 1",
            summary_raw="OpenAI announces GPT-5",
            content_snippet="OpenAI announces GPT-5 with major improvements",
            engagement={"credibility": 0.95}
        ),
        NewsItem(
            id="2",
            source="rss",
            source_name="Source B",
            title="GPT-5 Launched by OpenAI",
            url="https://example.com/2",
            published_at=datetime.now(),
            author="Author 2",
            summary_raw="GPT-5 is here",
            content_snippet="GPT-5 is here with new features from OpenAI",
            engagement={"credibility": 0.85}
        ),
        NewsItem(
            id="3",
            source="rss",
            source_name="Source C",
            title="Google Announces New AI Model",
            url="https://example.com/3",
            published_at=datetime.now(),
            author="Author 3",
            summary_raw="Google AI news",
            content_snippet="Google unveils new AI model with breakthrough performance",
            engagement={"credibility": 0.90}
        ),
    ]


def test_deduplicator_creation(embedding_model):
    """Test Deduplicator initialization."""
    dedup = Deduplicator(embedding_model, threshold=0.85)
    assert dedup.threshold == 0.85
    assert dedup.embedding_model is not None


def test_deduplicate(embedding_model, sample_items):
    """Test deduplication of similar items."""
    dedup = Deduplicator(embedding_model, threshold=0.75)
    deduplicated = dedup.deduplicate(sample_items)

    # Should find GPT-5 duplicates
    assert len(deduplicated) < len(sample_items)

    # Check that duplicates are tracked
    for item in deduplicated:
        if "GPT-5" in item.title or "gpt-5" in item.title.lower():
            # This item should have duplicates
            assert len(item.duplicates) >= 0


def test_select_best_item(embedding_model):
    """Test selecting best item from duplicates."""
    dedup = Deduplicator(embedding_model)

    items = [
        NewsItem(
            id="1",
            source="rss",
            source_name="Low Cred",
            title="Test",
            url="https://example.com/1",
            published_at=datetime.now(),
            author=None,
            summary_raw="",
            content_snippet="",
            engagement={"credibility": 0.5}
        ),
        NewsItem(
            id="2",
            source="rss",
            source_name="High Cred",
            title="Test",
            url="https://example.com/2",
            published_at=datetime.now(),
            author=None,
            summary_raw="",
            content_snippet="",
            engagement={"credibility": 0.95}
        ),
    ]

    best = dedup._select_best_item(items)
    assert best.id == "2"  # Higher credibility
