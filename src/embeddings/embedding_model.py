"""
Embedding Model — isolated behind a class interface for easy replacement.

Uses sentence-transformers/all-MiniLM-L6-v2 by default.
Implements graceful fallback: if the model can't load or inference fails,
the system continues with rule-based matching instead of crashing.

Design Decision:
    The EmbeddingModel class encapsulates all embedding logic so the matching
    engine never touches sentence-transformers directly. This makes it trivial
    to swap in a different model (OpenAI, Cohere, etc.) for V3.
"""

import logging
from typing import List, Optional

import numpy as np

from src.config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """
    Wrapper around sentence-transformers for generating text embeddings.

    Attributes:
        model_name: Name of the sentence-transformers model.
        available: Whether the model loaded successfully.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or EMBEDDING_MODEL
        self.available = False
        self._model = None

        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading embedding model: %s", self.model_name)
            self._model = SentenceTransformer(self.model_name)
            self.available = True
            logger.info("Embedding model loaded successfully.")
        except Exception as e:
            logger.warning(
                "Failed to load embedding model '%s': %s. "
                "Semantic matching will be unavailable. "
                "Falling back to rule-based matching only.",
                self.model_name,
                e,
            )

    def encode(self, texts: List[str]) -> Optional[np.ndarray]:
        """
        Encode a list of texts into embedding vectors.

        Args:
            texts: List of text strings to encode.

        Returns:
            A numpy array of shape (len(texts), embedding_dim),
            or None if the model is unavailable or encoding fails.
        """
        if not self.available or not self._model:
            return None

        if not texts:
            return None

        try:
            embeddings = self._model.encode(texts, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            logger.error(
                "Embedding inference failed: %s. "
                "Falling back to rule-based matching for this request.",
                e,
            )
            return None

    def cosine_similarity(self, embedding_a: np.ndarray, embedding_b: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embedding vectors.

        Args:
            embedding_a: First embedding vector.
            embedding_b: Second embedding vector.

        Returns:
            Cosine similarity score between 0 and 1.
        """
        # Handle multi-dimensional embeddings (average them)
        if embedding_a.ndim > 1:
            embedding_a = np.mean(embedding_a, axis=0)
        if embedding_b.ndim > 1:
            embedding_b = np.mean(embedding_b, axis=0)

        norm_a = np.linalg.norm(embedding_a)
        norm_b = np.linalg.norm(embedding_b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        similarity = float(np.dot(embedding_a, embedding_b) / (norm_a * norm_b))
        # Clamp to [0, 1] — negative cosine sim is treated as 0 (no match)
        return max(0.0, similarity)
