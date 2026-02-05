"""Main pipeline orchestrator for Neural Express."""

import asyncio
import os
from pathlib import Path
from datetime import datetime

from .config.settings import Settings
from .utils.logging import setup_logging, get_logger
from .utils.io import save_json, get_output_filename
from .utils.schema import NewsItem

from .ingestion.rss import fetch_rss_feed
from .ingestion.normalize import normalize_items
from .ingestion.mock_data import generate_mock_data

from .dedupe.embed import EmbeddingModel
from .dedupe.dedupe import Deduplicator

from .rank.select import (
    filter_by_time_window,
    rank_stories,
    select_top_stories,
    select_secondary_stories
)

from .summarize.llm import LLMClient
from .summarize.summarize import summarize_stories, generate_newsletter_intro

from .render.beehiiv_md import render_newsletter, save_newsletter
from .render.pdf_export import export_to_pdf
from .utils.email import send_newsletter_email


logger = get_logger("main")


class NeuralExpress:
    """Main pipeline for Neural Express."""

    def __init__(self, settings: Settings, verbose: bool = False, send_email: bool = False):
        """
        Initialize pipeline.

        Args:
            settings: Settings instance
            verbose: Enable verbose logging
            send_email: Send newsletter via email after generation
        """
        self.settings = settings
        self.send_email = send_email

        # Setup logging
        log_file = settings.output_dir / "neural_express.log"
        setup_logging(
            level=settings.log_level,
            log_file=log_file,
            verbose=verbose
        )

        logger.info("Initialized Neural Express pipeline")

    async def run(self, mode: str = "daily", use_mock: bool = False) -> str:
        """
        Run the complete pipeline.

        Args:
            mode: "daily" or "weekly"
            use_mock: Use mock data instead of fetching RSS feeds

        Returns:
            Path to generated newsletter file
        """
        logger.info(f"Starting Neural Express pipeline (mode: {mode})")

        # 1. Ingestion
        logger.info("=" * 50)
        logger.info("STEP 1: Ingestion")
        logger.info("=" * 50)

        if use_mock:
            items = generate_mock_data(count=20)
        else:
            items = await self._fetch_all_feeds()

        logger.info(f"Ingested {len(items)} total items")

        # Normalize
        items = normalize_items(items)

        # 2. Time filtering
        logger.info("=" * 50)
        logger.info("STEP 2: Time Filtering")
        logger.info("=" * 50)

        time_window = (
            self.settings.get("time_windows.daily", 24)
            if mode == "daily"
            else self.settings.get("time_windows.weekly", 168)
        )

        items = filter_by_time_window(items, time_window)

        # 3. Deduplication
        logger.info("=" * 50)
        logger.info("STEP 3: Deduplication")
        logger.info("=" * 50)

        embedding_model = EmbeddingModel(self.settings.embedding_model)
        story_chain_threshold = self.settings.get("dedupe.story_chain_threshold", 0.75)

        deduplicator = Deduplicator(
            embedding_model,
            threshold=self.settings.dedupe_threshold,
            story_chain_threshold=story_chain_threshold
        )

        # Use smart deduplication for weekly mode
        detect_chains = (mode == "weekly")
        items = deduplicator.deduplicate(items, detect_story_chains=detect_chains)

        # 4. Ranking
        logger.info("=" * 50)
        logger.info("STEP 4: Ranking")
        logger.info("=" * 50)

        relevance_keywords = self.settings.get("relevance_keywords", [])
        ranked_stories = rank_stories(
            items,
            self.settings.ranking_weights,
            time_window,
            relevance_keywords
        )

        # 5. Selection
        logger.info("=" * 50)
        logger.info("STEP 5: Selection")
        logger.info("=" * 50)

        top_stories = select_top_stories(
            ranked_stories,
            top_count=self.settings.top_stories_count,
            min_score=self.settings.get("selection.min_score", 0.3)
        )

        secondary_stories = select_secondary_stories(
            ranked_stories,
            top_stories,
            secondary_count=self.settings.secondary_stories_count,
            min_score=self.settings.get("selection.min_score", 0.2)
        )

        # 6. Summarization
        logger.info("=" * 50)
        logger.info("STEP 6: Summarization")
        logger.info("=" * 50)

        llm_client = LLMClient(
            api_key=self.settings.openai_api_key,
            model=self.settings.llm_model,
            temperature=self.settings.llm_temperature
        )

        top_stories = await summarize_stories(top_stories, llm_client)

        # Generate intro
        intro = generate_newsletter_intro(top_stories, llm_client)

        # Extract story chains for weekly mode
        story_chains = None
        if mode == "weekly":
            story_chains = self._extract_story_chains(top_stories + secondary_stories)

        # 7. Rendering
        logger.info("=" * 50)
        logger.info("STEP 7: Rendering")
        logger.info("=" * 50)

        newsletter = render_newsletter(
            top_stories,
            secondary_stories,
            intro,
            mode,
            story_chains
        )

        # 8. Save
        logger.info("=" * 50)
        logger.info("STEP 8: Saving Output")
        logger.info("=" * 50)

        output_filename = get_output_filename(mode, "md")
        output_path = self.settings.output_dir / output_filename

        # Save markdown
        save_newsletter(newsletter, str(output_path))

        # Save PDF
        pdf_path = output_path.with_suffix(".pdf")
        try:
            export_to_pdf(
                top_stories,
                secondary_stories,
                intro,
                pdf_path,
                mode,
                story_chains
            )
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")

        # Save metadata
        metadata = {
            "mode": mode,
            "generated_at": datetime.now().isoformat(),
            "total_items": len(items),
            "top_stories": len(top_stories),
            "secondary_stories": len(secondary_stories),
            "story_chains": len(story_chains) if story_chains else 0
        }

        metadata_path = output_path.with_suffix(".json")
        save_json(metadata, metadata_path)

        # 9. Email delivery
        if self.send_email:
            logger.info("=" * 50)
            logger.info("STEP 9: Email Delivery")
            logger.info("=" * 50)

            recipient = os.environ.get("EMAIL_RECIPIENT")
            if recipient:
                subject_template = self.settings.get(
                    "email.subject_template",
                    "NEURAL EXPRESS Weekly - {date}"
                )
                subject = subject_template.format(
                    date=datetime.now().strftime("%B %d, %Y")
                )

                pdf_attachment = str(pdf_path) if pdf_path.exists() else None
                success = send_newsletter_email(
                    to_email=recipient,
                    subject=subject,
                    body_text=newsletter,
                    pdf_path=pdf_attachment,
                )

                if success:
                    logger.info(f"Newsletter emailed to {recipient}")
                else:
                    logger.error(f"Failed to email newsletter to {recipient}")
            else:
                logger.warning("EMAIL_RECIPIENT not set, skipping email delivery")

        logger.info("=" * 50)
        logger.info("PIPELINE COMPLETE")
        logger.info("=" * 50)
        logger.info(f"Newsletter saved to: {output_path}")

        return str(output_path)

    async def _fetch_all_feeds(self) -> list[NewsItem]:
        """Fetch all RSS feeds."""
        feeds = self.settings.feeds

        logger.info(f"Fetching {len(feeds)} RSS feeds")

        tasks = [fetch_rss_feed(feed) for feed in feeds]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect items, log errors
        all_items = []
        errors = []

        for feed, result in zip(feeds, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch {feed['name']}: {result}")
                errors.append(feed["name"])
            else:
                all_items.extend(result)

        if errors:
            logger.warning(f"Failed feeds: {', '.join(errors)}")

        return all_items

    def _extract_story_chains(self, stories: list) -> dict:
        """
        Extract and group stories by chain ID.

        Args:
            stories: List of RankedStory objects

        Returns:
            Dict mapping chain_id to list of stories
        """
        story_chains = {}

        for story in stories:
            chain_id = story.news_item.story_chain_id
            if chain_id:
                if chain_id not in story_chains:
                    story_chains[chain_id] = []
                story_chains[chain_id].append(story)

        logger.info(f"Extracted {len(story_chains)} story chains")
        return story_chains
