"""Embedding utilities for semantic search."""

import os

# Set HuggingFace cache for Lambda compatibility (must be before imports)
# The model is pre-downloaded during Docker build to /var/task/models
if "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
    # Model is embedded in container at /var/task/models (set in Dockerfile)
    os.environ.setdefault("HF_HOME", "/var/task/models")
    os.environ.setdefault("TRANSFORMERS_CACHE", "/var/task/models")
    os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", "/var/task/models")

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Singleton service for generating query embeddings.

    Uses lazy loading to avoid loading the model until first use.
    Model is cached at class level for reuse across Lambda warm invocations.
    """

    _model: SentenceTransformer | None = None

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """Get or initialize the embedding model."""
        if cls._model is None:
            cls._model = SentenceTransformer("all-MiniLM-L6-v2")
        return cls._model

    @classmethod
    def embed_query(cls, query: str) -> list[float]:
        """Generate embedding for a search query.

        Args:
            query: Search query string.

        Returns:
            List of floats representing the embedding vector.
        """
        model = cls.get_model()
        return model.encode(query).tolist()
