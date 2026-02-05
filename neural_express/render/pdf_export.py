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
    KeepTogether,
    HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from ..utils.schema import RankedStory
from ..utils.logging import get_logger

logger = get_logger("render.pdf")

# Category emoji text mappings for PDF (reportlab can't render all emoji)
CATEGORY_LABELS = {
    "Chips": "[CHIPS]",
    "Hardware": "[CHIPS]",
    "Research": "[RESEARCH]",
    "Policy": "[POLICY]",
    "Tools": "[TOOLS]",
    "Business": "[BUSINESS]",
    "Funding": "[FUNDING]",
    "Robotics": "[ROBOTICS]",
    "AGI/Safety": "[AGI/SAFETY]",
    "Creative AI": "[CREATIVE AI]",
}

CATEGORY_COLORS = {
    "Chips": colors.HexColor('#e74c3c'),
    "Hardware": colors.HexColor('#e74c3c'),
    "Research": colors.HexColor('#3498db'),
    "Policy": colors.HexColor('#9b59b6'),
    "Tools": colors.HexColor('#e67e22'),
    "Business": colors.HexColor('#2ecc71'),
    "Funding": colors.HexColor('#f39c12'),
    "Robotics": colors.HexColor('#1abc9c'),
    "AGI/Safety": colors.HexColor('#e91e63'),
    "Creative AI": colors.HexColor('#ff6f61'),
}


class NewsletterPDF:
    """PDF newsletter generator with professional formatting."""

    def __init__(self, output_path: Path, mode: str = "daily"):
        self.output_path = output_path
        self.mode = mode
        self.doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch
        )
        self.story = []
        self.styles = self._create_styles()

    def _create_styles(self) -> dict:
        """Create custom paragraph styles."""
        styles = getSampleStyleSheet()

        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1a1a2e'),
            spaceAfter=4,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=34
        ))

        styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#666666'),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        ))

        styles.add(ParagraphStyle(
            name='DateRange',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#3498db'),
            spaceAfter=4,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        styles.add(ParagraphStyle(
            name='Greeting',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#333333'),
            spaceAfter=8,
            fontName='Helvetica',
            leading=16
        ))

        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1a1a2e'),
            spaceAfter=10,
            spaceBefore=16,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=colors.HexColor('#3498db'),
            borderPadding=4,
        ))

        styles.add(ParagraphStyle(
            name='StoryHeadline',
            parent=styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=6,
            spaceBefore=8,
            fontName='Helvetica-Bold',
            leading=17
        ))

        styles.add(ParagraphStyle(
            name='CategoryTag',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#ffffff'),
            spaceAfter=4,
            fontName='Helvetica-Bold',
        ))

        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leading=14
        ))

        styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#444444'),
            leftIndent=20,
            spaceAfter=4,
            leading=14
        ))

        styles.add(ParagraphStyle(
            name='TOCEntry',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            leftIndent=10,
            leading=15
        ))

        styles.add(ParagraphStyle(
            name='Source',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#888888'),
            spaceAfter=2
        ))

        styles.add(ParagraphStyle(
            name='FooterText',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#999999'),
            alignment=TA_CENTER,
            spaceAfter=4
        ))

        return styles

    def _get_date_range(self) -> str:
        end_date = datetime.now()
        if self.mode == "weekly":
            start_date = end_date - timedelta(days=10)
            return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        else:
            return end_date.strftime("%B %d, %Y")

    def _add_section_divider(self):
        """Add a horizontal rule divider."""
        self.story.append(Spacer(1, 0.1 * inch))
        self.story.append(HRFlowable(
            width="100%", thickness=1,
            color=colors.HexColor('#e0e0e0'),
            spaceAfter=8, spaceBefore=8
        ))

    def add_header(self, intro: str):
        """Section 1: Header with title, date range, tagline, greeting, overview."""
        self.story.append(Paragraph("NEURAL EXPRESS WEEKLY", self.styles['CustomTitle']))

        date_range = self._get_date_range()
        self.story.append(Paragraph(date_range, self.styles['DateRange']))

        tagline = "Your AI news briefing curated by intelligent agents"
        self.story.append(Paragraph(tagline, self.styles['CustomSubtitle']))

        self.story.append(Spacer(1, 0.15 * inch))

        if intro:
            self.story.append(Paragraph(intro, self.styles['Greeting']))

        self._add_section_divider()

    def add_in_this_issue(self, top_stories: List[RankedStory]):
        """Section 2: IN THIS ISSUE - numbered headlines with categories."""
        self.story.append(Paragraph("IN THIS ISSUE", self.styles['SectionHeader']))

        for i, story in enumerate(top_stories[:5], 1):
            if story.summary:
                headline = story.summary.headline
                category = story.summary.category
            else:
                headline = story.news_item.title
                category = "News"

            cat_label = CATEGORY_LABELS.get(category, "[NEWS]")
            toc_entry = f"<b>{i}.</b> {headline} <font color='#3498db'>{cat_label}</font>"
            self.story.append(Paragraph(toc_entry, self.styles['TOCEntry']))

        self._add_section_divider()

    def add_main_story(self, story: RankedStory, story_number: int):
        """Add a main story card with full details."""
        item = story.news_item

        # Use summary if available, fall back to raw data
        if story.summary:
            headline = story.summary.headline
            category = story.summary.category
            hook = story.summary.hook
            details = story.summary.details
            why_matters = story.summary.why_it_matters
            credit = story.summary.image_suggestion.credit_line
        else:
            headline = item.title
            category = "News"
            hook = item.summary_raw or item.content_snippet[:200]
            details = [item.content_snippet[:200]] if item.content_snippet else ["Details pending."]
            why_matters = f"A developing story from {item.source_name}."
            credit = f"Source: {item.source_name}"

        cat_label = CATEGORY_LABELS.get(category, "[NEWS]")
        cat_color = CATEGORY_COLORS.get(category, colors.HexColor('#333333'))

        story_elements = []

        # Story number + headline
        headline_text = f"<b>{story_number}. {cat_label} {headline}</b>"
        story_elements.append(Paragraph(headline_text, self.styles['StoryHeadline']))

        # Category and source line
        meta_line = f"<font color='{cat_color}'><b>{category}</b></font> | {item.source_name}"
        story_elements.append(Paragraph(meta_line, self.styles['Source']))
        story_elements.append(Spacer(1, 0.08 * inch))

        # Hook
        story_elements.append(Paragraph(hook, self.styles['CustomBody']))
        story_elements.append(Spacer(1, 0.08 * inch))

        # Details
        story_elements.append(Paragraph("<b>The details:</b>", self.styles['CustomBody']))
        for detail in details:
            # Escape XML special chars for reportlab
            safe_detail = detail.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story_elements.append(Paragraph(f"\u2022 {safe_detail}", self.styles['BulletPoint']))

        story_elements.append(Spacer(1, 0.08 * inch))

        # Why it matters
        safe_why = why_matters.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story_elements.append(Paragraph(f"<b>Why it matters:</b> {safe_why}", self.styles['CustomBody']))

        # Read more link
        source_text = f"<link href='{item.url}' color='blue'>Read more at {item.source_name}</link>"
        story_elements.append(Spacer(1, 0.04 * inch))
        story_elements.append(Paragraph(source_text, self.styles['Source']))

        # Add all story elements directly (no KeepTogether+Table nesting
        # which can overflow when content is tall)
        for el in story_elements:
            self.story.append(el)

        # Visual divider between stories
        self.story.append(Spacer(1, 0.08 * inch))
        self.story.append(HRFlowable(
            width="100%", thickness=0.5,
            color=colors.HexColor('#e0e0e0'),
            spaceAfter=8, spaceBefore=4
        ))
        self.story.append(Spacer(1, 0.08 * inch))

    def add_developing_stories(self, story_chains: dict):
        """Section 5: Developing stories with timelines."""
        if not story_chains:
            return

        self.story.append(PageBreak())
        self.story.append(Paragraph("DEVELOPING STORIES", self.styles['SectionHeader']))

        explanation = "Stories that evolved over multiple days this week."
        self.story.append(Paragraph(explanation, self.styles['CustomBody']))
        self.story.append(Spacer(1, 0.1 * inch))

        for chain_id, stories in story_chains.items():
            if len(stories) < 2:
                continue

            sorted_stories = sorted(stories, key=lambda s: s.news_item.published_at)

            first = sorted_stories[0]
            chain_title = first.summary.headline if first.summary else first.news_item.title
            self.story.append(Paragraph(f"<b>{chain_title}</b>", self.styles['StoryHeadline']))

            for story in sorted_stories:
                date_str = story.news_item.published_at.strftime("%b %d")
                headline = story.summary.headline if story.summary else story.news_item.title
                source = story.news_item.source_name

                safe_headline = headline.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                entry = f"\u2022 <b>{date_str}:</b> {safe_headline} <i>({source})</i>"
                self.story.append(Paragraph(entry, self.styles['BulletPoint']))

            # Add significance from latest story
            latest = sorted_stories[-1]
            if latest.summary:
                safe_sig = latest.summary.why_it_matters.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                self.story.append(Spacer(1, 0.05 * inch))
                self.story.append(Paragraph(f"<i>What it means: {safe_sig}</i>", self.styles['CustomBody']))

            self.story.append(Spacer(1, 0.15 * inch))

    def add_quick_bites(self, secondary_stories: List[RankedStory]):
        """Section 4: Quick bites."""
        if not secondary_stories:
            return

        self.story.append(PageBreak())
        self.story.append(Paragraph("QUICK BITES", self.styles['SectionHeader']))

        for story in secondary_stories:
            item = story.news_item

            if story.summary:
                headline = story.summary.headline
                snippet = story.summary.hook[:150]
            else:
                headline = item.title
                snippet = item.content_snippet[:150]

            safe_headline = headline.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            safe_snippet = snippet.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            quick_bite = f"\u2022 <b>{safe_headline}</b> \u2014 {safe_snippet} <i>({item.source_name})</i>"
            self.story.append(Paragraph(quick_bite, self.styles['BulletPoint']))
            self.story.append(Spacer(1, 0.06 * inch))

    def add_top_jobs(self):
        """Section 6: Top AI jobs."""
        self.story.append(Spacer(1, 0.2 * inch))
        self._add_section_divider()
        self.story.append(Paragraph("TOP AI JOBS THIS WEEK", self.styles['SectionHeader']))

        jobs = [
            ("Senior ML Engineer", "OpenAI", "San Francisco, CA", "Build next-gen language models"),
            ("AI Research Scientist", "Google DeepMind", "London, UK", "Advance AGI research"),
            ("Applied AI Lead", "Anthropic", "Remote", "Lead safety research initiatives"),
            ("Computer Vision Engineer", "Tesla", "Palo Alto, CA", "Autonomous driving AI"),
            ("NLP Engineer", "Meta", "Menlo Park, CA", "Large-scale NLP systems"),
        ]

        for title, company, location, description in jobs:
            job_text = f"\u2022 <b>{title}</b> at {company} \u2014 {location} \u2014 {description}"
            self.story.append(Paragraph(job_text, self.styles['BulletPoint']))
            self.story.append(Spacer(1, 0.05 * inch))

    def add_trending_tools(self):
        """Section 7: Trending AI tools."""
        self.story.append(Spacer(1, 0.2 * inch))
        self._add_section_divider()
        self.story.append(Paragraph("TRENDING AI TOOLS", self.styles['SectionHeader']))

        tools = [
            ("Claude Code", "AI-powered coding assistant for the terminal"),
            ("Midjourney v6", "State-of-the-art text-to-image generation"),
            ("LangChain", "Framework for building LLM applications"),
            ("Replicate", "Run and deploy ML models via API"),
            ("Weights &amp; Biases", "ML experiment tracking and visualization"),
        ]

        for tool_name, description in tools:
            tool_text = f"\u2022 <b>{tool_name}</b> \u2014 {description}"
            self.story.append(Paragraph(tool_text, self.styles['BulletPoint']))
            self.story.append(Spacer(1, 0.05 * inch))

    def add_sources(self, all_stories: List[RankedStory]):
        """Section 8: Sources."""
        self.story.append(PageBreak())
        self.story.append(Paragraph("SOURCES", self.styles['SectionHeader']))

        sources = []
        seen_urls = set()

        for story in all_stories:
            item = story.news_item
            if item.url not in seen_urls:
                sources.append((item.source_name, item.url))
                seen_urls.add(item.url)

        source_data = []
        for i, (source_name, url) in enumerate(sources, 1):
            display_url = url if len(url) < 70 else url[:67] + "..."
            source_data.append([f"{i}.", source_name, display_url])

        if source_data:
            source_table = Table(source_data, colWidths=[0.4 * inch, 1.8 * inch, 4.3 * inch])
            source_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#555555')),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#eeeeee')),
            ]))
            self.story.append(source_table)

    def add_footer(self):
        """Section 9: Footer."""
        self.story.append(Spacer(1, 0.4 * inch))
        self._add_section_divider()
        self.story.append(Spacer(1, 0.15 * inch))

        self.story.append(Paragraph(
            "Thanks for reading Neural Express!",
            self.styles['FooterText']
        ))
        self.story.append(Paragraph(
            "Reply to this email with feedback or questions.",
            self.styles['FooterText']
        ))
        self.story.append(Spacer(1, 0.1 * inch))
        self.story.append(Paragraph(
            "\u00a9 2026 Neural Express. All rights reserved.",
            self.styles['FooterText']
        ))
        self.story.append(Paragraph(
            "<i>Generated with Neural Express \u2014 AI-powered news curation</i>",
            self.styles['FooterText']
        ))

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
    Export newsletter to PDF with all 9 sections.

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

    # Section 1: Header
    pdf.add_header(intro)

    # Section 2: In This Issue
    pdf.add_in_this_issue(top_stories)

    # Section 3: Top Stories
    pdf.story.append(Paragraph("TOP STORIES", pdf.styles['SectionHeader']))
    for i, story in enumerate(top_stories, 1):
        pdf.add_main_story(story, i)

    # Section 4: Quick Bites
    pdf.add_quick_bites(secondary_stories)

    # Section 5: Developing Stories (weekly mode)
    if mode == "weekly" and story_chains:
        pdf.add_developing_stories(story_chains)

    # Section 6: Top AI Jobs
    pdf.add_top_jobs()

    # Section 7: Trending Tools
    pdf.add_trending_tools()

    # Section 8: Sources
    all_stories = top_stories + secondary_stories
    pdf.add_sources(all_stories)

    # Section 9: Footer
    pdf.add_footer()

    # Build PDF
    pdf.build()

    logger.info(f"PDF export complete: {output_path}")
