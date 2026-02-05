"""Deduplication logic using embeddings and clustering."""

from typing import Optional
import hashlib
import numpy as np
from datetime import timedelta
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity

from ..utils.schema import NewsItem
from ..utils.logging import get_logger
from .embed import EmbeddingModel
from .store import VectorStore

logger = get_logger("dedupe.dedupe")


class Deduplicator:
    """Handles deduplication of news items using embeddings."""

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        threshold: float = 0.85,
        story_chain_threshold: float = 0.75
    ):
        """
        Initialize deduplicator.

        Args:
            embedding_model: EmbeddingModel instance
            threshold: Similarity threshold for same-day duplicates (0-1)
            story_chain_threshold: Similarity threshold for story chains (0-1)
        """
        self.embedding_model = embedding_model
        self.threshold = threshold
        self.story_chain_threshold = story_chain_threshold
        logger.info(
            f"Initialized deduplicator with threshold {threshold}, "
            f"story chain threshold {story_chain_threshold}"
        )

    def deduplicate(
        self,
        items: list[NewsItem],
        detect_story_chains: bool = False
    ) -> list[NewsItem]:
        """
        Deduplicate news items by clustering similar content.

        Args:
            items: List of news items
            detect_story_chains: If True, detect and link story chains

        Returns:
            List of deduplicated news items (representatives from each cluster)
        """
        if not items:
            return []

        logger.info(f"Deduplicating {len(items)} items")

        # Generate embeddings for all items
        texts = [self._get_text_for_embedding(item) for item in items]
        embeddings = self.embedding_model.embed(texts)

        if detect_story_chains:
            # Smart deduplication with story chain detection
            deduplicated = self._smart_deduplicate(items, embeddings)
        else:
            # Standard deduplication
            clusters = self._cluster_embeddings(embeddings)
            deduplicated = self._select_representatives(items, clusters)

        logger.info(
            f"Deduplicated to {len(deduplicated)} items "
            f"({len(items) - len(deduplicated)} duplicates found)"
        )

        return deduplicated

    def _get_text_for_embedding(self, item: NewsItem) -> str:
        """
        Extract text for embedding generation.

        Args:
            item: News item

        Returns:
            Text string combining title and summary
        """
        return f"{item.title} {item.content_snippet}"

    def _cluster_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Cluster embeddings using agglomerative clustering.

        Args:
            embeddings: Array of embeddings (shape: [n, dimension])

        Returns:
            Array of cluster labels (shape: [n])
        """
        if len(embeddings) == 1:
            return np.array([0])

        # Convert similarity threshold to distance threshold
        # Cosine similarity to Euclidean distance for normalized vectors
        distance_threshold = np.sqrt(2 * (1 - self.threshold))

        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=distance_threshold,
            linkage="average",
            metric="euclidean"
        )

        # Normalize embeddings for cosine similarity via Euclidean distance
        embeddings_normalized = embeddings / np.linalg.norm(
            embeddings, axis=1, keepdims=True
        )

        labels = clustering.fit_predict(embeddings_normalized)

        logger.debug(f"Found {len(np.unique(labels))} clusters from {len(embeddings)} items")

        return labels

    def _select_representatives(
        self,
        items: list[NewsItem],
        clusters: np.ndarray
    ) -> list[NewsItem]:
        """
        Select representative item from each cluster.

        Args:
            items: List of news items
            clusters: Cluster labels for each item

        Returns:
            List of representative items (one per cluster)
        """
        representatives = []
        unique_clusters = np.unique(clusters)

        for cluster_id in unique_clusters:
            # Get all items in this cluster
            cluster_mask = clusters == cluster_id
            cluster_indices = np.where(cluster_mask)[0]
            cluster_items = [items[i] for i in cluster_indices]

            # Select representative (most credible, then most recent)
            representative = self._select_best_item(cluster_items)

            # Add duplicate URLs to representative
            representative.duplicates = [
                item.url for item in cluster_items
                if item.id != representative.id
            ]

            representatives.append(representative)

        return representatives

    def _select_best_item(self, items: list[NewsItem]) -> NewsItem:
        """
        Select best item from a group (highest credibility, then most recent).

        Args:
            items: List of news items

        Returns:
            Best news item
        """
        if len(items) == 1:
            return items[0]

        # Sort by credibility (descending), then by recency (descending)
        sorted_items = sorted(
            items,
            key=lambda x: (
                -x.engagement.get("credibility", 0.5),
                -x.published_at.timestamp()
            )
        )

        return sorted_items[0]

    def _smart_deduplicate(
        self,
        items: list[NewsItem],
        embeddings: np.ndarray
    ) -> list[NewsItem]:
        """
        Smart deduplication that detects story chains.

        High similarity + same day = DUPLICATE (remove)
        Medium similarity + different days = STORY CHAIN (keep & link)
        Low similarity = DIFFERENT stories (keep separate)

        Args:
            items: List of news items
            embeddings: Array of embeddings

        Returns:
            List of deduplicated items with story chains linked
        """
        logger.info("Running smart deduplication with story chain detection")

        # Normalize embeddings for cosine similarity
        embeddings_normalized = embeddings / np.linalg.norm(
            embeddings, axis=1, keepdims=True
        )

        # Compute similarity matrix
        similarity_matrix = cosine_similarity(embeddings_normalized)

        # Track which items to keep and which are duplicates
        keep_items = []
        processed = set()
        story_chains = {}  # chain_id -> list of item indices

        for i in range(len(items)):
            if i in processed:
                continue

            item_i = items[i]
            chain_members = [i]
            duplicates = []

            # Find similar items
            for j in range(i + 1, len(items)):
                if j in processed:
                    continue

                item_j = items[j]
                similarity = similarity_matrix[i][j]

                # Check time difference
                time_diff = abs((item_i.published_at - item_j.published_at).days)

                # High similarity + same day = DUPLICATE
                if similarity >= self.threshold and time_diff == 0:
                    duplicates.append(j)
                    processed.add(j)
                    logger.debug(
                        f"Duplicate found: '{item_i.title[:50]}' and '{item_j.title[:50]}' "
                        f"(similarity: {similarity:.3f}, same day)"
                    )

                # Medium similarity + different days = STORY CHAIN
                elif (
                    self.story_chain_threshold <= similarity < self.threshold
                    and time_diff > 0
                ):
                    chain_members.append(j)
                    logger.debug(
                        f"Story chain detected: '{item_i.title[:50]}' and '{item_j.title[:50]}' "
                        f"(similarity: {similarity:.3f}, {time_diff} days apart)"
                    )

            # Mark item as processed
            processed.add(i)

            # Keep the best item from duplicates
            duplicate_items = [items[j] for j in [i] + duplicates]
            best_item = self._select_best_item(duplicate_items)

            # Add duplicate URLs
            best_item.duplicates = [
                item.url for item in duplicate_items
                if item.id != best_item.id
            ]

            # Assign story chain ID if there are related stories
            if len(chain_members) > 1:
                # Generate unique chain ID
                chain_id = hashlib.md5(
                    f"{best_item.title[:50]}{best_item.published_at}".encode()
                ).hexdigest()[:8]

                best_item.story_chain_id = chain_id

                # Track chain members
                if chain_id not in story_chains:
                    story_chains[chain_id] = []
                story_chains[chain_id].extend(chain_members)

            keep_items.append(best_item)

        # Assign chain IDs to related stories
        for chain_id, member_indices in story_chains.items():
            for idx in member_indices:
                if idx < len(items) and items[idx] in keep_items:
                    items[idx].story_chain_id = chain_id

        logger.info(
            f"Smart deduplication complete: {len(keep_items)} items kept, "
            f"{len(story_chains)} story chains detected"
        )

        return keep_items


def build_vector_store(
    items: list[NewsItem],
    embedding_model: EmbeddingModel
) -> VectorStore:
    """
    Build vector store from news items.

    Args:
        items: List of news items
        embedding_model: EmbeddingModel instance

    Returns:
        Populated VectorStore
    """
    logger.info(f"Building vector store with {len(items)} items")

    # Create store
    store = VectorStore(dimension=embedding_model.dimension)

    if not items:
        return store

    # Generate embeddings
    texts = [f"{item.title} {item.content_snippet}" for item in items]
    embeddings = embedding_model.embed(texts)

    # Create metadata
    metadata = [
        {
            "id": item.id,
            "title": item.title,
            "url": item.url,
            "source_name": item.source_name
        }
        for item in items
    ]

    # Add to store
    store.add(embeddings, metadata)

    logger.info(f"Built vector store with {store.size()} vectors")

    return store
