"""PDF export for Neural Express newsletters."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from ..utils.schema import RankedStory
from ..utils.logging import get_logger

logger = get_logger("render.pdf")


class NewsletterPDF:
    """PDF newsletter generator."""

    def __init__(self, output_path: Path, mode: str = "daily"):
        """
        Initialize PDF generator.

        Args:
            output_path: Path to save PDF
            mode: "daily" or "weekly"
        """
        self.output_path = output_path
        self.mode = mode
        self.doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=1 * inch,
            bottomMargin=0.75 * inch
        )
        self.story = []
        self.styles = self._create_styles()

    def _create_styles(self) -> dict:
        """Create custom paragraph styles."""
        styles = getSampleStyleSheet()

        # Title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtitle style
        styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        ))

        # Section header
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))

        # Story headline
        styles.add(ParagraphStyle(
            name='StoryHeadline',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Body text
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leading=14
        ))

        # Bullet point
        styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#444444'),
            leftIndent=20,
            spaceAfter=4,
            leading=14
        ))

        # Source style
        styles.add(ParagraphStyle(
            name='Source',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            spaceAfter=2
        ))

        return styles

    def _get_date_range(self) -> str:
        """Get formatted date range for header."""
        end_date = datetime.now()

        if self.mode == "weekly":
            start_date = end_date - timedelta(days=10)
            return f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
        else:
            return end_date.strftime("%B %d, %Y")

    def add_header(self, intro: str):
        """Add newsletter header."""
        # Title
        title = f"NEURAL EXPRESS {self.mode.upper()}"
        self.story.append(Paragraph(title, self.styles['CustomTitle']))

        # Date range
        date_range = self._get_date_range()
        self.story.append(Paragraph(date_range, self.styles['CustomSubtitle']))

        # Tagline
        tagline = "Your AI news briefing curated by intelligent agents"
        self.story.append(Paragraph(tagline, self.styles['CustomSubtitle']))

        self.story.append(Spacer(1, 0.2 * inch))

        # Introduction
        if intro:
            self.story.append(Paragraph(intro, self.styles['CustomBody']))
            self.story.append(Spacer(1, 0.2 * inch))

    def add_executive_summary(self, top_stories: List[RankedStory]):
        """Add executive summary with top takeaways."""
        self.story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))

        takeaways = []
        for i, story in enumerate(top_stories[:5], 1):
            summary_text = story.summary.headline if story.summary else story.news_item.title
            takeaway = f"{i}. {summary_text}"
            takeaways.append(takeaway)

        for takeaway in takeaways:
            self.story.append(Paragraph(f"• {takeaway}", self.styles['BulletPoint']))

        self.story.append(Spacer(1, 0.2 * inch))

    def add_table_of_contents(self, top_stories: List[RankedStory]):
        """Add table of contents."""
        self.story.append(Paragraph("Table of Contents", self.styles['SectionHeader']))

        for i, story in enumerate(top_stories, 1):
            headline = story.summary.headline if story.summary else story.news_item.title
            category = story.summary.category if story.summary else "News"
            toc_entry = f"{i}. {headline} ({category})"
            self.story.append(Paragraph(toc_entry, self.styles['CustomBody']))

        self.story.append(Spacer(1, 0.3 * inch))

    def add_main_story(self, story: RankedStory, story_number: int):
        """Add a main story with full details."""
        item = story.news_item
        summary = story.summary

        if not summary:
            return

        # Category and headline
        category_emoji = self._get_category_emoji(summary.category)
        headline = f"{story_number}. {category_emoji} {summary.headline}"

        story_elements = []

        # Headline
        story_elements.append(Paragraph(headline, self.styles['StoryHeadline']))

        # Image placeholder
        image_credit = f"<i>{summary.image_suggestion.credit_line}</i>"
        story_elements.append(Paragraph(image_credit, self.styles['Source']))
        story_elements.append(Spacer(1, 0.1 * inch))

        # Hook
        story_elements.append(Paragraph(summary.hook, self.styles['CustomBody']))
        story_elements.append(Spacer(1, 0.1 * inch))

        # Details
        story_elements.append(Paragraph("<b>The details:</b>", self.styles['CustomBody']))
        for detail in summary.details:
            story_elements.append(Paragraph(f"• {detail}", self.styles['BulletPoint']))

        story_elements.append(Spacer(1, 0.1 * inch))

        # Why it matters
        why_matters = f"<b>Why it matters:</b> {summary.why_it_matters}"
        story_elements.append(Paragraph(why_matters, self.styles['CustomBody']))

        # Source link
        source_text = f"<link href='{item.url}' color='blue'>Read more at {item.source_name}</link>"
        story_elements.append(Spacer(1, 0.05 * inch))
        story_elements.append(Paragraph(source_text, self.styles['Source']))

        story_elements.append(Spacer(1, 0.2 * inch))

        # Keep story together on same page
        self.story.append(KeepTogether(story_elements))

    def add_developing_stories(self, story_chains: dict):
        """Add story evolution section for multi-day stories."""
        if not story_chains:
            return

        self.story.append(PageBreak())
        self.story.append(Paragraph("Developing Stories", self.styles['SectionHeader']))

        explanation = (
            "These stories evolved over multiple days. "
            "Each chain shows how a story developed throughout the week."
        )
        self.story.append(Paragraph(explanation, self.styles['CustomBody']))
        self.story.append(Spacer(1, 0.15 * inch))

        for chain_id, stories in story_chains.items():
            if len(stories) > 1:
                # Chain header
                first_story = stories[0]
                chain_title = first_story.summary.headline if first_story.summary else first_story.news_item.title
                self.story.append(Paragraph(f"<b>Story Chain:</b> {chain_title}", self.styles['StoryHeadline']))

                # Timeline
                for i, story in enumerate(sorted(stories, key=lambda s: s.news_item.published_at), 1):
                    date_str = story.news_item.published_at.strftime("%b %d")
                    headline = story.summary.headline if story.summary else story.news_item.title
                    source = story.news_item.source_name

                    timeline_entry = f"• <b>{date_str}:</b> {headline} <i>({source})</i>"
                    self.story.append(Paragraph(timeline_entry, self.styles['BulletPoint']))

                self.story.append(Spacer(1, 0.15 * inch))

    def add_quick_bites(self, secondary_stories: List[RankedStory]):
        """Add quick bites section."""
        if not secondary_stories:
            return

        self.story.append(PageBreak())
        self.story.append(Paragraph("Quick Bites", self.styles['SectionHeader']))

        for story in secondary_stories:
            item = story.news_item

            if story.summary:
                headline = story.summary.headline
                snippet = story.summary.hook[:150]
            else:
                headline = item.title
                snippet = item.content_snippet[:150]

            quick_bite = f"<b>{headline}</b> — {snippet} <i>({item.source_name})</i>"
            self.story.append(Paragraph(f"• {quick_bite}", self.styles['BulletPoint']))
            self.story.append(Spacer(1, 0.08 * inch))

    def add_top_jobs(self):
        """Add top AI jobs section (placeholder)."""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Top AI Roles This Week", self.styles['SectionHeader']))

        jobs = [
            ("Senior ML Engineer", "OpenAI", "San Francisco, CA - Build next-gen language models"),
            ("AI Research Scientist", "Google DeepMind", "London, UK - Advance AGI research"),
            ("Applied AI Lead", "Anthropic", "Remote - Lead safety research initiatives"),
            ("Computer Vision Engineer", "Tesla", "Palo Alto, CA - Autonomous driving AI"),
            ("NLP Engineer", "Meta", "Menlo Park, CA - Large-scale NLP systems"),
        ]

        for title, company, description in jobs:
            job_text = f"<b>{title}</b> at {company} — {description}"
            self.story.append(Paragraph(f"• {job_text}", self.styles['BulletPoint']))
            self.story.append(Spacer(1, 0.08 * inch))

    def add_trending_tools(self):
        """Add trending AI tools section (placeholder)."""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Trending AI Tools", self.styles['SectionHeader']))

        tools = [
            ("Claude 3.5 Sonnet", "Advanced AI assistant with extended context"),
            ("Midjourney v6", "State-of-the-art text-to-image generation"),
            ("LangChain", "Framework for building LLM applications"),
            ("Replicate", "Run and deploy ML models via API"),
            ("Weights & Biases", "ML experiment tracking and visualization"),
        ]

        for tool_name, description in tools:
            tool_text = f"<b>{tool_name}</b> — {description}"
            self.story.append(Paragraph(f"• {tool_text}", self.styles['BulletPoint']))
            self.story.append(Spacer(1, 0.08 * inch))

    def add_sources(self, all_stories: List[RankedStory]):
        """Add sources list."""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Sources", self.styles['SectionHeader']))

        # Collect unique sources
        sources = []
        seen_urls = set()

        for story in all_stories:
            item = story.news_item
            if item.url not in seen_urls:
                sources.append((item.source_name, item.url))
                seen_urls.add(item.url)

        # Create table
        source_data = []
        for i, (source_name, url) in enumerate(sources, 1):
            # Truncate long URLs
            display_url = url if len(url) < 80 else url[:77] + "..."
            source_data.append([f"{i}.", source_name, display_url])

        if source_data:
            source_table = Table(source_data, colWidths=[0.4 * inch, 1.8 * inch, 4.3 * inch])
            source_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))

            self.story.append(source_table)

    def add_footer(self):
        """Add newsletter footer."""
        self.story.append(Spacer(1, 0.3 * inch))

        footer_text = (
            "<i>Generated with Neural Express - "
            "AI-powered news curation by Claude Code</i>"
        )
        self.story.append(Paragraph(footer_text, self.styles['Source']))

    def _get_category_emoji(self, category: str) -> str:
        """Get emoji for category."""
        emojis = {
            "Chips": "💻",
            "Research": "🔬",
            "Policy": "⚖️",
            "Tools": "🛠️",
            "Business": "📢",
            "Funding": "💰"
        }
        return emojis.get(category, "📰")

    def build(self):
        """Build and save PDF."""
        try:
            self.doc.build(self.story)
            logger.info(f"Generated PDF: {self.output_path}")
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            raise


def export_to_pdf(
    top_stories: List[RankedStory],
    secondary_stories: List[RankedStory],
    intro: str,
    output_path: Path,
    mode: str = "daily",
    story_chains: Optional[dict] = None
) -> None:
    """
    Export newsletter to PDF.

    Args:
        top_stories: List of main stories
        secondary_stories: List of secondary stories
        intro: Newsletter introduction
        output_path: Path to save PDF
        mode: "daily" or "weekly"
        story_chains: Optional dict of story chains for developing stories
    """
    logger.info(f"Exporting newsletter to PDF: {output_path}")

    pdf = NewsletterPDF(output_path, mode)

    # Header
    pdf.add_header(intro)

    # Executive Summary
    pdf.add_executive_summary(top_stories)

    # Table of Contents
    pdf.add_table_of_contents(top_stories)

    # Main stories
    pdf.story.append(PageBreak())
    pdf.story.append(Paragraph("Latest Developments", pdf.styles['SectionHeader']))

    for i, story in enumerate(top_stories, 1):
        pdf.add_main_story(story, i)

    # Developing stories (if weekly mode)
    if mode == "weekly" and story_chains:
        pdf.add_developing_stories(story_chains)

    # Quick bites
    pdf.add_quick_bites(secondary_stories)

    # Jobs and tools
    pdf.add_top_jobs()
    pdf.add_trending_tools()

    # Sources
    all_stories = top_stories + secondary_stories
    pdf.add_sources(all_stories)

    # Footer
    pdf.add_footer()

    # Build PDF
    pdf.build()

    logger.info(f"PDF export complete: {output_path}")
