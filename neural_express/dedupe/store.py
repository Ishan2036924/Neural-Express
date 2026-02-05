"""FAISS vector store for similarity search."""

from typing import Optional
from pathlib import Path
import numpy as np
import faiss

from ..utils.logging import get_logger
from ..utils.io import save_pickle, load_pickle

logger = get_logger("dedupe.store")


class VectorStore:
    """FAISS-based vector store for similarity search."""

    def __init__(self, dimension: int):
        """
        Initialize vector store.

        Args:
            dimension: Embedding dimension
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata: list[dict] = []

        logger.info(f"Initialized FAISS index with dimension {dimension}")

    def add(self, embeddings: np.ndarray, metadata: list[dict]) -> None:
        """
        Add vectors to the index.

        Args:
            embeddings: NumPy array of embeddings (shape: [n, dimension])
            metadata: List of metadata dicts (length: n)
        """
        if len(embeddings) != len(metadata):
            raise ValueError("Number of embeddings must match metadata length")

        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Embedding dimension {embeddings.shape[1]} doesn't match index dimension {self.dimension}")

        # Normalize embeddings for cosine similarity
        embeddings_normalized = embeddings.astype(np.float32)
        faiss.normalize_L2(embeddings_normalized)

        # Add to index
        self.index.add(embeddings_normalized)
        self.metadata.extend(metadata)

        logger.debug(f"Added {len(embeddings)} vectors to index")

    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 10,
        threshold: Optional[float] = None
    ) -> list[tuple[dict, float]]:
        """
        Search for similar vectors.

        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            threshold: Optional similarity threshold (cosine similarity)

        Returns:
            List of (metadata, similarity_score) tuples
        """
        if query_embedding.shape[0] != self.dimension:
            raise ValueError(f"Query dimension {query_embedding.shape[0]} doesn't match index dimension {self.dimension}")

        # Normalize query
        query_normalized = query_embedding.astype(np.float32).reshape(1, -1)
        faiss.normalize_L2(query_normalized)

        # Search
        distances, indices = self.index.search(query_normalized, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # No more results
                break

            # Convert L2 distance to cosine similarity
            # After normalization: L2^2 = 2(1 - cosine_similarity)
            similarity = 1 - (dist / 2)

            # Apply threshold if specified
            if threshold is not None and similarity < threshold:
                continue

            results.append((self.metadata[idx], float(similarity)))

        return results

    def search_batch(
        self,
        query_embeddings: np.ndarray,
        k: int = 10,
        threshold: Optional[float] = None
    ) -> list[list[tuple[dict, float]]]:
        """
        Batch search for similar vectors.

        Args:
            query_embeddings: Array of query embeddings (shape: [n, dimension])
            k: Number of results per query
            threshold: Optional similarity threshold

        Returns:
            List of lists of (metadata, similarity_score) tuples
        """
        # Normalize queries
        queries_normalized = query_embeddings.astype(np.float32)
        faiss.normalize_L2(queries_normalized)

        # Search
        distances, indices = self.index.search(queries_normalized, k)

        all_results = []
        for query_distances, query_indices in zip(distances, indices):
            results = []
            for dist, idx in zip(query_distances, query_indices):
                if idx == -1:
                    break

                similarity = 1 - (dist / 2)

                if threshold is not None and similarity < threshold:
                    continue

                results.append((self.metadata[idx], float(similarity)))

            all_results.append(results)

        return all_results

    def size(self) -> int:
        """Get number of vectors in the index."""
        return self.index.ntotal

    def save(self, filepath: Path) -> None:
        """
        Save index and metadata to disk.

        Args:
            filepath: Path to save file (will create .index and .metadata files)
        """
        index_path = filepath.with_suffix(".index")
        metadata_path = filepath.with_suffix(".metadata")

        # Save FAISS index
        faiss.write_index(self.index, str(index_path))

        # Save metadata
        save_pickle(self.metadata, metadata_path)

        logger.info(f"Saved vector store to {filepath}")

    def load(self, filepath: Path) -> None:
        """
        Load index and metadata from disk.

        Args:
            filepath: Path to load file (will load .index and .metadata files)
        """
        index_path = filepath.with_suffix(".index")
        metadata_path = filepath.with_suffix(".metadata")

        if not index_path.exists() or not metadata_path.exists():
            logger.warning(f"Vector store files not found at {filepath}")
            return

        # Load FAISS index
        self.index = faiss.read_index(str(index_path))

        # Load metadata
        self.metadata = load_pickle(metadata_path) or []

        logger.info(f"Loaded vector store from {filepath} ({self.size()} vectors)")
