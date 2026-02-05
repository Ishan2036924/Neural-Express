# NEURAL EXPRESS - System Architecture

**Technical Design Document**

This document provides a comprehensive overview of the Neural Express system architecture, data flow, algorithms, and design decisions.

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Data Flow](#data-flow)
3. [Module Architecture](#module-architecture)
4. [Core Algorithms](#core-algorithms)
5. [Data Schemas](#data-schemas)
6. [Configuration System](#configuration-system)
7. [Error Handling](#error-handling)
8. [Performance Considerations](#performance-considerations)

---

## 🌐 System Overview

Neural Express is a multi-stage pipeline that transforms raw RSS feeds into professionally formatted newsletters. The system prioritizes:

- **Reliability**: Graceful handling of feed failures
- **Intelligence**: Smart deduplication and story chain detection
- **Quality**: AI-powered summarization and professional formatting
- **Efficiency**: Async operations and local embeddings
- **Flexibility**: Configurable weights, thresholds, and outputs

### Key Design Principles

1. **Fail-Safe Operations**: Individual feed failures don't stop the pipeline
2. **Local-First AI**: Embeddings run locally to minimize API costs
3. **Dual Output**: Both Markdown (for Beehiiv) and PDF (for distribution)
4. **Story Intelligence**: Detects both duplicates and evolving narratives
5. **Transparent Ranking**: Multi-factor scoring with clear weights

---

## 🔄 Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         NEURAL EXPRESS PIPELINE                      │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│ 1. INGESTION │  Fetch from 40+ RSS feeds in parallel
└──────┬───────┘
       │  Raw articles (2000+ items)
       ↓
┌──────────────┐
│ 2. NORMALIZE │  Clean and standardize to canonical schema
└──────┬───────┘
       │  NewsItem objects
       ↓
┌──────────────┐
│ 3. TIME      │  Filter by time window (24h daily, 10d weekly)
│    FILTER    │
└──────┬───────┘
       │  Recent items (200-300 items)
       ↓
┌──────────────┐
│ 4. DEDUPE    │  Generate embeddings → Cluster → Detect chains
└──────┬───────┘
       │  Unique items with chain IDs (150-200 items)
       ↓
┌──────────────┐
│ 5. RANKING   │  Multi-factor scoring (recency, credibility, etc.)
└──────┬───────┘
       │  Ranked stories with scores
       ↓
┌──────────────┐
│ 6. SELECTION │  Pick top 5 + secondary 10 stories
└──────┬───────┘
       │  Selected stories
       ↓
┌──────────────┐
│ 7. SUMMARIZE │  OpenAI GPT-4o-mini generates summaries
└──────┬───────┘
       │  Stories with AI summaries
       ↓
┌──────────────┐
│ 8. RENDER    │  Generate Markdown + PDF newsletters
└──────┬───────┘
       │
       ↓
┌──────────────────────────────────────┐
│  OUTPUT: .md + .pdf + .json files    │
└──────────────────────────────────────┘
```

---

## 🏗️ Module Architecture

### 1. **config/** - Configuration Management

**Purpose**: Centralized configuration loading and validation

**Files:**
- `settings.py` - Settings class with environment variable support
- `default.yaml` - Default configuration with all RSS feeds and parameters

**Key Features:**
- YAML-based configuration
- Environment variable overrides (.env file)
- Validation on startup
- Hierarchical config access (e.g., `settings.get("ranking.weights")`)

**Example Usage:**
```python
settings = Settings()
feeds = settings.feeds  # List of RSS feed configs
weights = settings.ranking_weights  # Ranking weights dict
```

---

### 2. **ingestion/** - Data Collection

**Purpose**: Fetch and normalize news from multiple sources

**Files:**
- `rss.py` - Async RSS feed fetching with httpx
- `arxiv.py` - arXiv API integration (optional)
- `normalize.py` - Data cleaning and standardization
- `mock_data.py` - Test data generation

**Data Flow:**
```
RSS Feed → feedparser → Raw Entry → normalize → NewsItem
```

**Key Features:**
- Parallel async fetching of all feeds
- Automatic HTML tag stripping
- Date parsing with multiple fallbacks
- Graceful error handling (continue on failure)
- Credibility scores per source

**Error Handling:**
- HTTP errors logged but don't stop pipeline
- Feed parsing errors caught per entry
- Timeout handling (30s default)

---

### 3. **dedupe/** - Deduplication & Embeddings

**Purpose**: Eliminate duplicate stories and detect evolving narratives

**Files:**
- `embed.py` - Sentence-transformers wrapper
- `store.py` - FAISS vector store
- `dedupe.py` - Clustering and story chain detection

#### Deduplication Algorithm

**Standard Mode (Daily):**
```
1. Generate embeddings for all items (title + content)
2. Normalize vectors for cosine similarity
3. Agglomerative clustering with threshold 0.85
4. Select best representative from each cluster
   - Criteria: Highest credibility, then most recent
```

**Smart Mode (Weekly):**
```
1. Generate embeddings for all items
2. Compute full similarity matrix
3. For each pair of items:

   IF similarity > 0.9 AND same_day:
      → DUPLICATE (remove lower quality)

   ELSE IF 0.75 < similarity < 0.9 AND different_days:
      → STORY CHAIN (keep both, assign chain_id)

   ELSE IF similarity < 0.75:
      → DIFFERENT STORIES (keep separate)

4. Group stories by chain_id for rendering
```

**Example Story Chain:**
```
Day 1: "OpenAI announces GPT-5" (similarity: 0.80)
Day 3: "GPT-5 now available via API" (similarity: 0.78)
Day 7: "GPT-5 reaches 10M users" (similarity: 0.75)

→ All 3 kept and linked with chain_id: "a3f5c2d8"
```

**Technology:**
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (384 dims)
- **Vector Store**: FAISS IndexFlatL2
- **Clustering**: sklearn AgglomerativeClustering

---

### 4. **rank/** - Scoring & Selection

**Purpose**: Rank stories by importance and select top content

**Files:**
- `score.py` - Individual scoring functions
- `select.py` - Story selection logic

#### Ranking Formula

```python
score = (w_recency × recency_score) +
        (w_credibility × credibility_score) +
        (w_engagement × engagement_score) +
        (w_uniqueness × uniqueness_score) +
        (w_relevance × relevance_score)

# Default weights:
w_recency = 0.30      # Time-sensitive news
w_credibility = 0.25  # Trust in source
w_engagement = 0.15   # Future: upvotes, comments
w_uniqueness = 0.15   # Inverse of cluster size
w_relevance = 0.15    # AI/ML keyword density
```

#### Scoring Components

**1. Recency Score (0-1):**
```python
if age_hours <= time_window:
    score = 1.0
else:
    excess = age_hours - time_window
    score = 0.5 ^ (excess / (time_window × 0.1))  # Exponential decay
```

**2. Credibility Score (0-1):**
```python
score = source_credibility  # From config
# MIT Tech Review: 0.95
# TechCrunch: 0.85
# Personal blogs: 0.70
```

**3. Engagement Score (0-1):**
```python
# Currently placeholder (0.5)
# Future: (upvotes + comments + shares) / normalization_factor
```

**4. Uniqueness Score (0-1):**
```python
cluster_size = 1 + len(duplicates)
score = 1.0 / cluster_size

# Unique story: 1.0
# Story with 3 duplicates: 0.25
```

**5. Relevance Score (0-1):**
```python
text = title + content_snippet
matches = count_keywords(text, AI_KEYWORDS)
density = matches / len(AI_KEYWORDS)
score = min(1.0, density × 2)  # Cap at 1.0

AI_KEYWORDS = ["artificial intelligence", "machine learning",
               "deep learning", "neural network", "llm", ...]
```

**Selection Logic:**
```
1. Sort all stories by score (descending)
2. Filter by min_score threshold (0.3)
3. Select top N stories (default: 5)
4. Select next M stories for secondary section (default: 10)
```

---

### 5. **summarize/** - AI-Powered Content Generation

**Purpose**: Generate professional story summaries using LLM

**Files:**
- `prompts.py` - Prompt templates
- `llm.py` - OpenAI API wrapper
- `summarize.py` - Summarization pipeline

#### LLM Integration

**Model**: OpenAI GPT-4o-mini
- **Cost**: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- **Speed**: ~2-4 seconds per story
- **Temperature**: 0.7 (balanced creativity)

**Prompt Structure:**
```
You are an AI news editor creating concise, engaging summaries.

ARTICLE:
Title: {title}
Source: {source_name}
Content: {content[:2000]}

INSTRUCTIONS:
1. Create catchy headline (under 70 chars)
2. Write 1-2 line hook
3. Provide 3-6 key detail bullets
4. Explain why this matters (2-4 lines)
5. Categorize: Chips|Research|Policy|Tools|Business|Funding
6. Suggest image keywords and credit

Output JSON:
{
  "headline": "...",
  "hook": "...",
  "details": ["...", "..."],
  "why_it_matters": "...",
  "category": "...",
  "image_suggestion": {...}
}
```

**Error Handling:**
- JSON parsing failures logged and skipped
- API timeouts retry once
- Rate limiting handled with backoff
- Failed summaries don't stop pipeline

---

### 6. **render/** - Output Generation

**Purpose**: Create professional newsletters in multiple formats

**Files:**
- `templates.py` - Markdown template constants
- `beehiiv_md.py` - Markdown newsletter generator
- `pdf_export.py` - Professional PDF generator

#### Markdown Format (Beehiiv-Compatible)

```markdown
# NEURAL EXPRESS

*Your daily briefing on the AI stories that matter*

[Introduction paragraph]

In today's NEURAL EXPRESS:
- [TOC items]

---

## LATEST DEVELOPMENTS

### 🔬 [Headline]
*Image credit*

[Hook paragraph]

**The details:**
- Bullet 1
- Bullet 2

**Why it matters:** [Explanation]

[Read more](url)

---

## Everything else in AI today
- **Story** — Brief summary [(Source)](url)

---

### Sources
[Complete list]
```

#### PDF Format (Professional Multi-Page)

**Structure:**
1. **Header**
   - Title: "NEURAL EXPRESS WEEKLY"
   - Date range: "January 26 - February 04, 2026"
   - Tagline

2. **Executive Summary**
   - Top 5 takeaways as bullets

3. **Table of Contents**
   - All main stories with categories

4. **Main Stories**
   - Full formatting with:
     - Category emoji + headline
     - Image credit placeholder
     - Hook paragraph
     - Details bullets
     - Why it matters
     - Source link

5. **Developing Stories** (Weekly only)
   - Story chains grouped
   - Timeline showing evolution
   - Example: "Story Chain: SpaceX/xAI Merger"
     - Feb 3: Initial announcement
     - Feb 4: Regulatory filing details

6. **Quick Bites**
   - Secondary stories (one-liners)

7. **Top AI Jobs**
   - Curated job listings (placeholder)

8. **Trending Tools**
   - Popular AI tools (placeholder)

9. **Sources**
   - Table with all article links

**Styling:**
- Custom fonts (Helvetica Bold/Regular)
- Color scheme: Dark headers (#2c3e50), gray body (#333333)
- Professional spacing and margins
- KeepTogether for story integrity

---

### 7. **utils/** - Shared Utilities

**Purpose**: Common schemas, logging, and I/O operations

**Files:**
- `schema.py` - Dataclass definitions
- `logging.py` - Structured logging setup
- `io.py` - File operations (JSON, pickle, markdown)

---

## 📊 Data Schemas

### NewsItem
```python
@dataclass
class NewsItem:
    id: str                    # MD5 hash of URL
    source: str                # "rss" | "arxiv"
    source_name: str           # "TechCrunch AI"
    title: str
    url: str
    published_at: datetime
    author: Optional[str]
    summary_raw: str           # Original summary
    content_snippet: str       # First 500 chars
    tags: list[str]            # ["ai", "ml"]
    engagement: dict           # {"credibility": 0.85}
    duplicates: list[str]      # URLs of duplicates
    story_chain_id: Optional[str]  # Links related stories
```

### StorySummary
```python
@dataclass
class StorySummary:
    headline: str              # Refined title
    hook: str                  # 1-2 line intro
    details: list[str]         # 3-6 bullets
    why_it_matters: str        # 2-4 lines
    category: str              # Classification
    image_suggestion: ImageSuggestion
```

### RankedStory
```python
@dataclass
class RankedStory:
    news_item: NewsItem
    score: float               # Composite score
    recency_score: float
    credibility_score: float
    engagement_score: float
    uniqueness_score: float
    relevance_score: float
    summary: Optional[StorySummary]
```

---

## ⚙️ Configuration System

### Hierarchy

1. **Default Config** (`config/default.yaml`)
2. **Custom Config** (via `--config` flag)
3. **Environment Variables** (`.env` file)

### Key Settings

```yaml
# RSS Feeds (40 sources)
feeds:
  - name: TechCrunch AI
    url: https://techcrunch.com/...
    credibility: 0.85

# Time Windows
time_windows:
  daily: 24       # hours
  weekly: 240     # 10 days

# Deduplication
dedupe:
  threshold: 0.85               # Same-day duplicates
  story_chain_threshold: 0.75   # Multi-day chains

# Ranking
ranking:
  weights:
    recency: 0.30
    credibility: 0.25
    engagement: 0.15
    uniqueness: 0.15
    relevance: 0.15

# Selection
selection:
  top_stories: 5
  secondary_stories: 10
  min_score: 0.3

# LLM
llm:
  model: gpt-4o-mini
  temperature: 0.7
  max_tokens: 1000
```

---

## 🛡️ Error Handling

### Strategy: Continue on Failure

**Philosophy**: Individual component failures should not stop the entire pipeline.

### Feed Ingestion
```python
# Parallel fetching with exception handling
results = await asyncio.gather(*tasks, return_exceptions=True)

for feed, result in zip(feeds, results):
    if isinstance(result, Exception):
        logger.error(f"Failed {feed['name']}: {result}")
        continue  # Skip this feed, continue with others
    else:
        all_items.extend(result)
```

### LLM Summarization
```python
# Individual story failure doesn't stop pipeline
for story in stories:
    try:
        summary = llm_client.generate_json(prompt)
        story.summary = parse_summary(summary)
    except Exception as e:
        logger.warning(f"Failed to summarize: {e}")
        # Story continues without summary
        continue
```

### PDF Generation
```python
# PDF failure doesn't prevent Markdown output
try:
    export_to_pdf(stories, output_path)
except Exception as e:
    logger.error(f"PDF generation failed: {e}")
    # Markdown still saved successfully
```

---

## ⚡ Performance Considerations

### Optimization Strategies

**1. Async Operations**
- All RSS fetching done in parallel with `asyncio.gather()`
- HTTP requests use async httpx client
- Typical: 40 feeds fetched in ~5 seconds

**2. Local Embeddings**
- sentence-transformers runs locally (no API calls)
- GPU acceleration if available (CUDA)
- Batch embedding for efficiency

**3. Efficient Deduplication**
- FAISS for fast similarity search
- Normalized vectors for cosine similarity
- In-memory operations (no disk I/O)

**4. Minimal API Calls**
- Only 5-10 OpenAI API calls per run (stories + intro)
- Total cost: ~$0.002-0.003 per newsletter

**5. Caching (Future)**
- Could cache embeddings for historical articles
- Could cache feed content for retry logic

### Bottlenecks

1. **LLM Summarization** (~15-25 seconds)
   - Solution: Could parallelize with async OpenAI calls

2. **Embedding Generation** (~3-5 seconds for 200 items)
   - Solution: GPU acceleration or batch size tuning

3. **RSS Parsing** (~5-10 seconds)
   - Already optimized with async

---

## 🔮 Future Enhancements

### Architecture Improvements

1. **Database Integration**
   - Store historical articles for trend analysis
   - Enable article search and filtering

2. **Microservices**
   - Separate ingestion, processing, rendering
   - Enable horizontal scaling

3. **Event-Driven**
   - Process articles as they arrive
   - Real-time newsletter updates

4. **Caching Layer**
   - Redis for feed content
   - Reduce redundant API calls

5. **Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Alert on feed failures

### Feature Additions

1. **Image Processing**
   - Fetch and embed actual images
   - Image deduplication
   - Automatic thumbnail generation

2. **Sentiment Analysis**
   - Track positive/negative trends
   - Highlight controversial stories

3. **Topic Modeling**
   - Automatic categorization beyond keywords
   - Trend detection over time

4. **Multi-Language**
   - Translate summaries
   - Multi-language RSS feeds

---

## 📚 References

### Papers & Documentation

- **Sentence Transformers**: [Reimers & Gurevych, 2019](https://arxiv.org/abs/1908.10084)
- **FAISS**: [Johnson et al., 2019](https://github.com/facebookresearch/faiss)
- **Agglomerative Clustering**: [Scikit-learn docs](https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering)
- **OpenAI API**: [OpenAI Platform](https://platform.openai.com/docs)

### Code Standards

- **Style**: Black (line length: 88)
- **Linting**: Ruff
- **Type Hints**: Python 3.10+ with dataclasses
- **Docstrings**: Google-style
- **Testing**: pytest with coverage

---

**Last Updated**: February 4, 2026
**Version**: 2.0.0 (with story chains + PDF)
