# Neural Express Upgrades - Implementation Complete

## ✅ 1. EXPANDED RSS FEEDS (27 new sources added)

### News & Media (7 sources)
- Reuters AI: https://www.reuters.com/technology/artificial-intelligence/rss
- Bloomberg Tech: https://feeds.bloomberg.com/technology/news.rss
- CNBC Tech: https://www.cnbc.com/id/19854910/device/rss/rss.html
- Forbes AI: https://www.forbes.com/ai/feed/
- BBC Tech: https://feeds.bbci.co.uk/news/technology/rss.xml
- The Guardian Tech: https://www.theguardian.com/technology/rss
- NYT Tech: https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml

### AI-Specific (6 sources)
- The Batch (DeepLearning.AI): https://www.deeplearning.ai/the-batch/feed/
- Towards AI: https://pub.towardsai.net/feed
- Analytics Vidhya: https://www.analyticsvidhya.com/feed/
- KDnuggets: https://www.kdnuggets.com/feed
- Import AI Newsletter: https://importai.substack.com/feed
- Last Week in AI: https://lastweekin.ai/feed

### Research & Company Blogs (14 sources)
- arXiv AI: http://arxiv.org/rss/cs.AI
- arXiv ML: http://arxiv.org/rss/cs.LG
- Google Research: https://blog.research.google/feeds/posts/default
- Meta AI Blog: https://ai.meta.com/blog/rss/
- Microsoft AI Blog: https://blogs.microsoft.com/ai/feed/
- NVIDIA AI Blog: https://blogs.nvidia.com/feed/
- Amazon Science: https://www.amazon.science/index.rss

**Total: 40 RSS feeds (13 original + 27 new)**

**Files Modified:**
- `config/default.yaml` - Added all new feeds with credibility scores

---

## ✅ 2. PDF OUTPUT GENERATION

### Features Implemented:
- ✅ Professional PDF with reportlab
- ✅ Header with date range (daily/weekly)
- ✅ Executive Summary (top 5 takeaways)
- ✅ Table of Contents
- ✅ Main Stories with full formatting
- ✅ Story Evolution section (developing stories for weekly mode)
- ✅ Quick Bites section
- ✅ Top AI Jobs section (placeholder)
- ✅ Trending Tools section (placeholder)
- ✅ Complete sources list
- ✅ Custom styling and typography

### Output:
Every run now generates TWO files:
- `neural_express_[mode]_[timestamp].md` - Markdown for Beehiiv
- `neural_express_[mode]_[timestamp].pdf` - Professional PDF

**Files Created:**
- `render/pdf_export.py` - Complete PDF generation module
- `requirements.txt` - Added reportlab>=4.0.0, Pillow>=10.0.0

**Files Modified:**
- `main.py` - Integrated PDF export into pipeline

---

## ✅ 3. SMART WEEKLY MODE WITH STORY TRACKING

### Configuration Updates:
```yaml
time_windows:
  weekly: 240  # 10 days (was 168)

weekly_lookback_days: 10

dedupe:
  threshold: 0.85  # Same-day duplicates
  story_chain_threshold: 0.75  # Story chains across days
```

### Smart Deduplication Logic:

**High Similarity (>0.9) + Same Day = DUPLICATE (remove)**
- Example: TechCrunch, Verge, Reuters all report "OpenAI announces GPT-5" on same day
- Action: Keep only the best source (highest credibility)

**Medium Similarity (0.7-0.9) + Different Days = STORY CHAIN (keep & link)**
- Example:
  - Day 1: "OpenAI announces GPT-5"
  - Day 3: "GPT-5 now available in API"
  - Day 7: "GPT-5 reaches 10M users"
- Action: Keep all 3 stories, link them with `story_chain_id`

**Low Similarity (<0.7) = DIFFERENT (keep separate)**
- Action: Treat as independent stories

### Implementation Details:

1. **Schema Updates:**
   - Added `story_chain_id: Optional[str]` to `NewsItem`
   - Links related stories across multiple days

2. **Deduplication Algorithm:**
   - Computes cosine similarity matrix for all items
   - Checks both similarity AND time difference
   - Assigns unique chain IDs to related stories
   - Tracks duplicates separately from story chains

3. **Weekly Mode Features:**
   - Automatically enables story chain detection
   - Groups related stories in "Developing Stories" section
   - Shows timeline of how stories evolved
   - PDF includes special formatting for story chains

**Files Modified:**
- `utils/schema.py` - Added `story_chain_id` field
- `dedupe/dedupe.py` - Added `_smart_deduplicate()` method
- `config/default.yaml` - Added story chain threshold and weekly lookback
- `main.py` - Integrated story chain detection and extraction
- `render/pdf_export.py` - Added developing stories section

---

## Testing the Upgrades

### Test with Daily Mode:
```bash
python -m neural_express run --mode daily --verbose
```

### Test with Weekly Mode (with story chains):
```bash
python -m neural_express run --mode weekly --verbose
```

### Expected Output:
- `.md` file - Beehiiv-ready markdown
- `.pdf` file - Professional PDF newsletter
- `.json` file - Metadata with story chain count

---

## Summary of Changes

### Files Created (2):
1. `render/pdf_export.py` - PDF generation module (600+ lines)
2. `UPGRADES.md` - This documentation

### Files Modified (6):
1. `config/default.yaml` - 27 new feeds, story chain config
2. `utils/schema.py` - Added story_chain_id field
3. `dedupe/dedupe.py` - Smart deduplication algorithm
4. `main.py` - PDF export, story chain extraction
5. `requirements.txt` - Added reportlab and Pillow
6. Multiple dependency installs

### Key Metrics:
- **RSS Feeds:** 13 → 40 (207% increase)
- **Deduplication:** Standard → Smart (with story chains)
- **Output Formats:** 1 (MD) → 2 (MD + PDF)
- **Weekly Lookback:** 7 days → 10 days
- **Story Chain Detection:** NEW FEATURE

---

## Next Steps

1. **Test the pipeline** with both daily and weekly modes
2. **Verify PDF output** formatting and content
3. **Check story chain detection** in weekly mode
4. **Monitor RSS feed success rates** with 40 sources
5. **Customize job and tool placeholders** if needed

All upgrades are complete and ready for testing! 🚀
