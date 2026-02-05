"""Mock data generator for testing."""

import hashlib
from datetime import datetime, timedelta
from ..utils.schema import NewsItem


def generate_mock_data(count: int = 20) -> list[NewsItem]:
    """
    Generate mock news items for testing.

    Args:
        count: Number of items to generate

    Returns:
        List of mock NewsItem objects
    """
    mock_stories = [
        {
            "title": "OpenAI Releases GPT-5 with Enhanced Reasoning Capabilities",
            "source_name": "OpenAI Blog",
            "credibility": 0.95,
            "summary": "OpenAI announces GPT-5, featuring breakthrough improvements in reasoning, mathematics, and code generation.",
            "tags": ["llm", "openai", "gpt"]
        },
        {
            "title": "Google DeepMind Achieves New Breakthrough in Protein Folding",
            "source_name": "MIT Technology Review",
            "credibility": 0.95,
            "summary": "AlphaFold 3 demonstrates unprecedented accuracy in predicting protein structures and drug interactions.",
            "tags": ["research", "protein-folding", "deepmind"]
        },
        {
            "title": "Anthropic Raises $2B in Series D Funding",
            "source_name": "TechCrunch AI",
            "credibility": 0.85,
            "summary": "AI safety company Anthropic secures $2 billion in funding to advance constitutional AI research.",
            "tags": ["funding", "anthropic", "ai-safety"]
        },
        {
            "title": "Meta Releases Open-Source Multimodal Model Llama 4",
            "source_name": "VentureBeat AI",
            "credibility": 0.85,
            "summary": "Meta's latest Llama model supports text, image, and audio inputs with competitive performance.",
            "tags": ["open-source", "multimodal", "meta"]
        },
        {
            "title": "NVIDIA Unveils Next-Gen AI Chips with 10x Performance Boost",
            "source_name": "The Verge AI",
            "credibility": 0.80,
            "summary": "NVIDIA's new H200 GPUs deliver unprecedented performance for training large language models.",
            "tags": ["chips", "nvidia", "hardware"]
        },
        {
            "title": "EU Passes Comprehensive AI Regulation Act",
            "source_name": "Reuters Tech",
            "credibility": 0.95,
            "summary": "European Union approves sweeping AI regulations focusing on safety and transparency.",
            "tags": ["policy", "regulation", "eu"]
        },
        {
            "title": "Microsoft Copilot Now Integrated Across Office Suite",
            "source_name": "Microsoft Blog",
            "credibility": 0.90,
            "summary": "Microsoft expands AI assistant capabilities to all Office applications with new features.",
            "tags": ["tools", "microsoft", "copilot"]
        },
        {
            "title": "Startup Introduces AI Agent for Automated Code Review",
            "source_name": "The Rundown AI",
            "credibility": 0.75,
            "summary": "New developer tool uses AI agents to automatically review and suggest code improvements.",
            "tags": ["agents", "developer-tools", "startup"]
        },
        {
            "title": "Study Shows AI Models Can Develop Emergent Reasoning Abilities",
            "source_name": "MIT Technology Review",
            "credibility": 0.95,
            "summary": "New research reveals how large language models develop unexpected reasoning capabilities.",
            "tags": ["research", "reasoning", "emergent-behavior"]
        },
        {
            "title": "OpenAI Launches ChatGPT Enterprise for Businesses",
            "source_name": "OpenAI Blog",
            "credibility": 0.95,
            "summary": "OpenAI introduces enterprise version of ChatGPT with enhanced security and customization.",
            "tags": ["business", "chatgpt", "enterprise"]
        },
    ]

    items = []
    base_time = datetime.now()

    for i in range(min(count, len(mock_stories))):
        story = mock_stories[i]
        url = f"https://example.com/article-{i}"
        item_id = hashlib.md5(url.encode()).hexdigest()

        # Stagger publication times
        published_at = base_time - timedelta(hours=i * 2)

        item = NewsItem(
            id=item_id,
            source="rss",
            source_name=story["source_name"],
            title=story["title"],
            url=url,
            published_at=published_at,
            author="Mock Author",
            summary_raw=story["summary"],
            content_snippet=story["summary"][:500],
            tags=story["tags"],
            engagement={"credibility": story["credibility"]}
        )

        items.append(item)

    # Generate duplicates for some items (for testing deduplication)
    if count > len(mock_stories):
        for i in range(count - len(mock_stories)):
            original_idx = i % len(items)
            original = items[original_idx]

            # Create slight variation
            url = f"https://different-site.com/article-{i}"
            item_id = hashlib.md5(url.encode()).hexdigest()

            duplicate = NewsItem(
                id=item_id,
                source="rss",
                source_name="Different Source",
                title=original.title + " - Updated",  # Slight title variation
                url=url,
                published_at=original.published_at + timedelta(hours=1),
                author=original.author,
                summary_raw=original.summary_raw,
                content_snippet=original.content_snippet,
                tags=original.tags,
                engagement={"credibility": 0.75}
            )

            items.append(duplicate)

    return items
