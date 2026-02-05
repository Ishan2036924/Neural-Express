# NEURAL EXPRESS

**Automated AI News Research + Newsletter Drafting Engine**

Neural Express is an intelligent news curation system that automatically ingests AI news from 40+ RSS feeds, detects duplicate stories and evolving narratives, ranks content by relevance, generates AI-powered summaries, and outputs professional Beehiiv-ready newsletters in both Markdown and PDF formats.

---

## ✨ Features

- 🌐 **Multi-Source Ingestion** - Fetches from 40+ RSS feeds including major tech publications, AI blogs, and research outlets
- 🧠 **Smart Deduplication** - Uses sentence-transformers embeddings + FAISS to eliminate duplicate stories
- 🔗 **Story Chain Detection** - Automatically links related stories across multiple days (weekly mode)
- 📊 **Intelligent Ranking** - Multi-factor scoring based on recency, credibility, engagement, uniqueness, and relevance
- 🤖 **AI-Powered Summarization** - Generates headlines, hooks, details, and insights using OpenAI GPT-4o-mini
- 📄 **Dual Output Formats** - Produces both Beehiiv-ready Markdown and professional PDF newsletters
- ⚡ **Daily & Weekly Modes** - Flexible time windows (24h for daily, 10 days for weekly)
- 📈 **Comprehensive Analytics** - Tracks story chains, duplicate detection, and source performance

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd neural_express_project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Configuration

Edit `.env` file:

```bash
OPENAI_API_KEY=sk-your-key-here
NEURAL_EXPRESS_OUTPUT_DIR=./output
NEURAL_EXPRESS_LOG_LEVEL=INFO
```

### Run

```bash
# Daily newsletter (last 24 hours)
python -m neural_express run --mode daily

# Weekly newsletter (last 10 days with story chains)
python -m neural_express run --mode weekly

# With verbose logging
python -m neural_express run --mode daily --verbose

# Test with mock data (no API calls)
python -m neural_express run --mode daily --mock
```

---

## 📖 Usage Examples

### Daily Mode

Generates a newsletter from the last 24 hours of AI news:

```bash
python -m neural_express run --mode daily --verbose
```

**Output:**
- `output/neural_express_daily_YYYYMMDD_HHMMSS.md` - Markdown newsletter
- `output/neural_express_daily_YYYYMMDD_HHMMSS.pdf` - PDF newsletter
- `output/neural_express_daily_YYYYMMDD_HHMMSS.json` - Metadata

### Weekly Mode

Generates a newsletter from the last 10 days with story chain detection:

```bash
python -m neural_express run --mode weekly --verbose
```

**Unique Features:**
- Detects story chains (related stories evolving over multiple days)
- Groups developing stories in "Developing Stories" section
- Shows timeline of how stories evolved
- Longer lookback period (10 days vs 24 hours)

### Custom Configuration

```bash
# Use custom config file
python -m neural_express run --mode daily --config custom_config.yaml

# Custom output directory
python -m neural_express run --mode weekly --output ./newsletters
```

---

## 📡 RSS Feeds

Neural Express monitors **40 RSS feeds** across 3 categories:

### Original Feeds (13)
- TechCrunch AI
- VentureBeat AI
- MIT Technology Review
- The Verge AI
- Ars Technica AI
- Wired AI
- The Rundown AI
- AI News
- Google AI Blog
- OpenAI Blog
- Anthropic News
- Hugging Face Blog
- Reuters Tech

### News & Media (7)
- Reuters AI
- Bloomberg Tech
- CNBC Tech
- Forbes AI
- BBC Tech
- The Guardian Tech
- NYT Tech

### AI-Specific Publications (6)
- The Batch (DeepLearning.AI)
- Towards AI
- Analytics Vidhya
- KDnuggets
- Import AI Newsletter
- Last Week in AI

### Research & Company Blogs (14)
- arXiv AI (cs.AI)
- arXiv Machine Learning (cs.LG)
- Google Research Blog
- Meta AI Blog
- Microsoft AI Blog
- NVIDIA AI Blog
- Amazon Science

**Note:** Some feeds may have authentication requirements or redirect issues. The system gracefully handles failures and continues processing available sources.

---

## 🏗️ Tech Stack

### Core Technologies
- **Python 3.10+** - Primary language
- **asyncio** - Async RSS fetching
- **feedparser** - RSS/Atom feed parsing
- **httpx** - Async HTTP client

### AI/ML
- **OpenAI GPT-4o-mini** - Story summarization and newsletter generation
- **sentence-transformers** - Local embeddings (all-MiniLM-L6-v2)
- **FAISS** - Vector similarity search for deduplication
- **scikit-learn** - Agglomerative clustering

### Data Processing
- **numpy** - Numerical operations
- **pandas** - Data manipulation
- **pydantic** - Data validation

### Output Generation
- **reportlab** - Professional PDF generation
- **Pillow** - Image processing for PDFs

### Utilities
- **python-dotenv** - Environment management
- **pyyaml** - Configuration files
- **click** - CLI interface
- **rich** - Terminal formatting

---

## 📊 Output Format

### Markdown Newsletter
```markdown
# NEURAL EXPRESS

*Your daily/weekly briefing on the AI stories that matter*

In today's NEURAL EXPRESS:
- [Top story headlines]

## LATEST DEVELOPMENTS

### 🔬 [Story Headline]
*Image credit line*

[Hook paragraph]

**The details:**
- Key point 1
- Key point 2
- Key point 3

**Why it matters:** [Significance explanation]

## Everything else in AI today
- Brief story mentions

### Sources
[Complete list of source URLs]
```

### PDF Newsletter
Professional multi-page PDF with:
- Header with date range
- Executive Summary (top 5 takeaways)
- Table of Contents
- Main Stories (full formatting)
- Developing Stories (weekly mode only)
- Quick Bites
- Top AI Jobs
- Trending Tools
- Complete Sources List

---

## 🔧 Configuration

Customize behavior in `config/default.yaml`:

```yaml
# Time windows
time_windows:
  daily: 24      # hours
  weekly: 240    # 10 days

# Deduplication
dedupe:
  threshold: 0.85               # Same-day duplicates
  story_chain_threshold: 0.75   # Story chains

# Ranking weights
ranking:
  weights:
    recency: 0.30
    credibility: 0.25
    engagement: 0.15
    uniqueness: 0.15
    relevance: 0.15

# Story selection
selection:
  top_stories: 5
  secondary_stories: 10
  min_score: 0.3
```

---

## 🧪 Testing

```bash
# Run with mock data (no API calls)
python -m neural_express run --mode daily --mock

# Run unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=neural_express --cov-report=html

# Code formatting
black neural_express/

# Linting
ruff check neural_express/
```

---

## 📁 Project Structure

```
neural_express_project/
├── neural_express/          # Main package
│   ├── config/             # Configuration management
│   ├── ingestion/          # RSS/arXiv fetching
│   ├── dedupe/             # Deduplication & embeddings
│   ├── rank/               # Scoring & selection
│   ├── summarize/          # LLM summarization
│   ├── render/             # Markdown & PDF output
│   └── utils/              # Shared utilities
├── tests/                  # Unit tests
├── output/                 # Generated newsletters
├── requirements.txt        # Dependencies
├── README.md              # This file
├── ARCHITECTURE.md        # System design docs
└── .env                   # Environment variables
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests before committing
pytest tests/ -v

# Format code
black neural_express/
ruff check neural_express/
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Missing OpenAI API Key**
```bash
# Error: OPENAI_API_KEY not set
# Solution: Add key to .env file
echo "OPENAI_API_KEY=sk-your-key" >> .env
```

**2. RSS Feed Failures**
- Some feeds require authentication or have changed URLs
- Pipeline continues on failure and logs warnings
- Check logs in `output/neural_express.log`

**3. Out of Memory**
- Reduce `time_windows.weekly` in config
- Process fewer feeds by editing `config/default.yaml`

**4. PDF Generation Fails**
```bash
# Reinstall reportlab
pip install --upgrade reportlab Pillow
```

### Getting Help

- Check logs: `output/neural_express.log`
- Run with verbose: `--verbose` flag
- Review `ARCHITECTURE.md` for system details
- Open an issue on GitHub

---

## 📈 Performance

Typical run metrics:

**Daily Mode:**
- Fetches: ~50-100 articles
- Runtime: ~30 seconds
- OpenAI tokens: ~3,000 tokens (~$0.002)
- Output: ~6-8 KB (Markdown), ~15-20 KB (PDF)

**Weekly Mode:**
- Fetches: ~200-300 articles
- Runtime: ~45 seconds
- OpenAI tokens: ~3,500 tokens (~$0.003)
- Story chains: 5-10 detected
- Output: ~10-12 KB (Markdown), ~20-25 KB (PDF)

---

## 📝 License

MIT License

Copyright (c) 2026 Neural Express

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🙏 Acknowledgments

Built with:
- [OpenAI](https://openai.com) - GPT-4o-mini for summarization
- [Sentence Transformers](https://www.sbert.net/) - Local embeddings
- [FAISS](https://github.com/facebookresearch/faiss) - Vector search
- [ReportLab](https://www.reportlab.com/) - PDF generation
- [Claude Code](https://claude.com/claude-code) - Development assistance

---

## 🚀 Future Enhancements

- [ ] Email delivery integration (SendGrid/Mailgun)
- [ ] Web dashboard for newsletter preview
- [ ] Social media integration (Twitter/LinkedIn auto-posting)
- [ ] Historical trend analysis
- [ ] Custom RSS feed management UI
- [ ] Multi-language support
- [ ] Sentiment analysis integration
- [ ] Image fetching and embedding
- [ ] A/B testing for headlines

---

**Made with ❤️ for the AI community**
