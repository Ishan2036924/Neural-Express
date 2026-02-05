"""Configuration management for Neural Express."""

import os
from pathlib import Path
from typing import Any, Optional
import yaml
from dotenv import load_dotenv

from ..utils.logging import get_logger

logger = get_logger("config")

# Load environment variables
load_dotenv()


class Settings:
    """Application settings manager."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize settings.

        Args:
            config_path: Path to custom config file (optional)
        """
        # Load default config
        if config_path is None:
            config_path = Path(__file__).parent / "default.yaml"

        self.config = self._load_config(config_path)

        # Environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.output_dir = Path(os.getenv("NEURAL_EXPRESS_OUTPUT_DIR", "./output"))
        self.log_level = os.getenv("NEURAL_EXPRESS_LOG_LEVEL", "INFO")

        # Validate
        self._validate()

    def _load_config(self, config_path: Path) -> dict:
        """Load configuration from YAML file."""
        if not config_path.exists():
            logger.error(f"Config file not found: {config_path}")
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        logger.info(f"Loaded config from {config_path}")
        return config

    def _validate(self) -> None:
        """Validate required settings."""
        if not self.openai_api_key:
            logger.error("OPENAI_API_KEY not set in environment")
            raise ValueError(
                "OPENAI_API_KEY is required. "
                "Set it in .env file or environment variables."
            )

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    @property
    def feeds(self) -> list[dict]:
        """Get RSS feed configurations."""
        return self.get("feeds", [])

    @property
    def ranking_weights(self) -> dict:
        """Get ranking weights."""
        return self.get("ranking.weights", {})

    @property
    def llm_model(self) -> str:
        """Get LLM model name."""
        return self.get("llm.model", "gpt-4o-mini")

    @property
    def llm_temperature(self) -> float:
        """Get LLM temperature."""
        return self.get("llm.temperature", 0.7)

    @property
    def embedding_model(self) -> str:
        """Get embedding model name."""
        return self.get("embeddings.model", "sentence-transformers/all-MiniLM-L6-v2")

    @property
    def dedupe_threshold(self) -> float:
        """Get deduplication similarity threshold."""
        return self.get("dedupe.threshold", 0.85)

    @property
    def top_stories_count(self) -> int:
        """Get number of top stories to select."""
        return self.get("selection.top_stories", 5)

    @property
    def secondary_stories_count(self) -> int:
        """Get number of secondary stories to include."""
        return self.get("selection.secondary_stories", 10)
