"""Embedding utilities for semantic search."""

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
