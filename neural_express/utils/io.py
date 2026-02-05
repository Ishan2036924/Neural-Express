"""File I/O utilities for Neural Express."""

import json
import pickle
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

from .logging import get_logger

logger = get_logger("io")


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists, create if necessary."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json(data: Any, filepath: Path, indent: int = 2) -> None:
    """
    Save data as JSON file.

    Args:
        data: Data to save (must be JSON-serializable)
        filepath: Path to save file
        indent: JSON indentation level
    """
    ensure_dir(filepath.parent)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str)

    logger.debug(f"Saved JSON to {filepath}")


def load_json(filepath: Path) -> Any:
    """
    Load data from JSON file.

    Args:
        filepath: Path to JSON file

    Returns:
        Loaded data
    """
    if not filepath.exists():
        logger.warning(f"JSON file not found: {filepath}")
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    logger.debug(f"Loaded JSON from {filepath}")
    return data


def save_pickle(data: Any, filepath: Path) -> None:
    """
    Save data as pickle file.

    Args:
        data: Data to save
        filepath: Path to save file
    """
    ensure_dir(filepath.parent)

    with open(filepath, "wb") as f:
        pickle.dump(data, f)

    logger.debug(f"Saved pickle to {filepath}")


def load_pickle(filepath: Path) -> Optional[Any]:
    """
    Load data from pickle file.

    Args:
        filepath: Path to pickle file

    Returns:
        Loaded data or None if file doesn't exist
    """
    if not filepath.exists():
        logger.warning(f"Pickle file not found: {filepath}")
        return None

    with open(filepath, "rb") as f:
        data = pickle.load(f)

    logger.debug(f"Loaded pickle from {filepath}")
    return data


def save_markdown(content: str, filepath: Path) -> None:
    """
    Save markdown content to file.

    Args:
        content: Markdown content
        filepath: Path to save file
    """
    ensure_dir(filepath.parent)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Saved markdown to {filepath}")


def get_output_filename(mode: str, extension: str = "md") -> str:
    """
    Generate timestamped output filename.

    Args:
        mode: "daily" or "weekly"
        extension: File extension (default: "md")

    Returns:
        Filename string
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"neural_express_{mode}_{timestamp}.{extension}"
