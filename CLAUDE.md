# CLAUDE.md - Neural Express Project

## Project Overview
NEURAL EXPRESS is an automated AI news research + newsletter drafting engine.
- Ingests AI news from RSS feeds
- Normalizes to canonical schema
- Deduplicates using local embeddings (sentence-transformers) + FAISS
- Summarizes with OpenAI GPT-4o-mini
- Ranks and selects top stories
- Generates Beehiiv-ready Markdown drafts

## Tech Decisions
- **LLM**: OpenAI GPT-4o-mini (cheap, good quality)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (FREE, local)
- **Vector Store**: FAISS (in-memory, with pickle persistence option)
- **HTTP**: httpx (async support)
- **RSS**: feedparser
- **Error Handling**: Continue on source failure, log warnings, report at end

## Project Structure
```
neural_express/
├── __init__.py
├── __main__.py
├── main.py
├── config/
│   ├── __init__.py
│   ├── default.yaml
│   └── settings.py
├── ingestion/
│   ├── __init__.py
│   ├── rss.py
│   ├── arxiv.py
│   ├── normalize.py
│   └── mock_data.py
├── dedupe/
│   ├── __init__.py
│   ├── embed.py
│   ├── dedupe.py
│   └── store.py
├── summarize/
│   ├── __init__.py
│   ├── prompts.py
│   ├── llm.py
│   └── summarize.py
├── rank/
│   ├── __init__.py
│   ├── score.py
│   └── select.py
├── render/
│   ├── __init__.py
│   ├── beehiiv_md.py
│   └── templates.py
└── utils/
    ├── __init__.py
    ├── schema.py
    ├── io.py
    └── logging.py
tests/
├── __init__.py
├── test_schema.py
├── test_dedupe.py
├── test_rank.py
└── test_render.py
.env.example
requirements.txt
README.md
```

## Canonical News Item Schema
```python
@dataclass
class NewsItem:
    id: str                    # stable hash of url
    source: str                # "rss" | "arxiv"
    source_name: str           # "TechCrunch", "MIT Tech Review"
    title: str
    url: str
    published_at: datetime     # ISO8601
    author: str | None
    summary_raw: str           # from source
    content_snippet: str       # first ~500 chars
    tags: list[str]            # ["AI Chips", "Agents"]
    engagement: dict           # {"upvotes": None, "reddit_score": None}
    duplicates: list[str]      # URLs of duplicate articles (added during dedupe)
```

## RSS Feeds to Include
```yaml
feeds:
  - name: TechCrunch AI
    url: https://techcrunch.com/category/artificial-intelligence/feed/
    credibility: 0.85
  - name: VentureBeat AI
    url: https://venturebeat.com/category/ai/feed/
    credibility: 0.85
  - name: MIT Technology Review
    url: https://www.technologyreview.com/feed/
    credibility: 0.95
  - name: The Verge AI
    url: https://www.theverge.com/rss/ai-artificial-intelligence/index.xml
    credibility: 0.80
  - name: Ars Technica AI
    url: https://feeds.arstechnica.com/arstechnica/technology-lab
    credibility: 0.85
  - name: Wired AI
    url: https://www.wired.com/feed/tag/ai/latest/rss
    credibility: 0.85
  - name: The Rundown AI
    url: https://www.therundown.ai/feed
    credibility: 0.75
  - name: AI News
    url: https://www.artificialintelligence-news.com/feed/
    credibility: 0.70
  - name: Google AI Blog
    url: https://blog.google/technology/ai/rss/
    credibility: 0.95
  - name: OpenAI Blog
    url: https://openai.com/blog/rss/
    credibility: 0.95
  - name: Anthropic News
    url: https://www.anthropic.com/news/rss
    credibility: 0.95
  - name: Hugging Face Blog
    url: https://huggingface.co/blog/feed.xml
    credibility: 0.90
  - name: Reuters Tech
    url: https://www.reutersagency.com/feed/?best-topics=tech
    credibility: 0.95
```

## Ranking Formula
```
score = (w_recency * recency_score) + 
        (w_credibility * source_credibility) +
        (w_engagement * engagement_score) +
        (w_uniqueness * uniqueness_score) +
        (w_relevance * relevance_score)

Default weights:
  recency: 0.30
  credibility: 0.25
  engagement: 0.15
  uniqueness: 0.15
  relevance: 0.15

recency_score: 1.0 if < 24h (daily) or < 7d (weekly), decay after
uniqueness_score: 1.0 / cluster_size
relevance_score: keyword match density for AI/ML/LLM/GenAI terms
```

## Beehiiv Draft Format
```markdown
# NEURAL EXPRESS

*Your daily briefing on the AI stories that matter*

Good morning, Reader 👋

In today's NEURAL EXPRESS:
- [Headline 1 summary]
- [Headline 2 summary]
- ...

---

## LATEST DEVELOPMENTS

### 📢 {Headline 1}

*Image source: {Company/Source}*

{1-2 line hook paragraph}

**The details:**
- {bullet 1}
- {bullet 2}
- {bullet 3}

**Why it matters:** {2-4 lines explaining significance}

---

[Repeat for each main story]

---

## Everything else in AI today

- **{Short headline}** — {One line summary} [(Source)]({url})
- ...

---

## Top AI roles this week

- **{Role Title}** at {Company} — {Brief description}
- ...

---

## Trending AI tools

- **{Tool Name}** — {One line description} [(Link)]({url})
- ...

---

### Sources
{List of all source URLs}

### Image Credits
{List of image sources}
```

## Summary Schema (LLM Output)
```python
@dataclass
class StorySummary:
    headline: str              # refined title
    hook: str                  # 1-2 line intro
    details: list[str]         # 3-6 bullets
    why_it_matters: str        # 2-4 lines
    category: str              # Chips|Research|Policy|Tools|Business|Funding
    image_suggestion: ImageSuggestion

@dataclass  
class ImageSuggestion:
    search_keywords: list[str]  # 3-6 keywords
    credit_line: str            # "Image source: Microsoft"
    source_url: str | None      # official image URL if known
    fallback_banner: bool       # True if no official source
```

## CLI Interface
```bash
# Main command
python -m neural_express run --mode daily|weekly [--config path] [--mock] [--output dir]

# Options:
#   --mode      daily (24h) or weekly (7d)
#   --config    custom config file path
#   --mock      use mock data (no API calls)
#   --output    custom output directory
#   --verbose   detailed logging
```

## Environment Variables
```
OPENAI_API_KEY=sk-...
NEURAL_EXPRESS_OUTPUT_DIR=./output
NEURAL_EXPRESS_LOG_LEVEL=INFO
```

## Build Order
1. utils/schema.py - Dataclasses and type definitions
2. utils/logging.py - Structured logging setup
3. utils/io.py - File I/O helpers
4. config/settings.py - Config loader
5. config/default.yaml - Default configuration
6. ingestion/rss.py - RSS feed fetcher
7. ingestion/arxiv.py - arXiv API (optional)
8. ingestion/normalize.py - Map to canonical schema
9. ingestion/mock_data.py - Mock data for testing
10. dedupe/embed.py - Sentence transformer embeddings
11. dedupe/store.py - FAISS vector store
12. dedupe/dedupe.py - Clustering logic
13. rank/score.py - Scoring functions
14. rank/select.py - Selection logic
15. summarize/prompts.py - LLM prompt templates
16. summarize/llm.py - OpenAI client wrapper
17. summarize/summarize.py - Summarization pipeline
18. render/templates.py - Markdown templates
19. render/beehiiv_md.py - Final renderer
20. main.py - Pipeline orchestrator
21. __main__.py - CLI entrypoint
22. tests/* - Unit tests
23. README.md - Documentation