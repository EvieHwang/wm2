"""Product lookup tool with semantic search and keyword fallback."""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional

import pandas as pd

from src.data.reference_loader import get_reference_data

# Flag to enable/disable semantic search (disabled in Lambda until container deployed)
SEMANTIC_SEARCH_ENABLED = os.environ.get("SEMANTIC_SEARCH_ENABLED", "true").lower() == "true"

# Logger for this module
import logging
logger = logging.getLogger(__name__)


class KeywordSearcher:
    """Keyword-based search fallback for Lambda deployment."""

    @staticmethod
    def search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search reference data using keyword matching.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.

        Returns:
            List of matching product dictionaries.
        """
        if not query or not query.strip():
            return []

        df = get_reference_data()
        query_lower = query.lower()
        keywords = query_lower.split()

        matches = []
        for idx, row in df.iterrows():
            searchable_parts = [
                str(row.get("Product Name", "")),
                str(row.get("Category", "")),
                str(row.get("About Product", "")),
            ]
            searchable = " ".join(searchable_parts).lower()

            score = sum(1 for kw in keywords if kw in searchable)
            product_name = str(row.get("Product Name", "")).lower()

            if query_lower in product_name:
                score += 5
            elif any(kw in product_name for kw in keywords):
                score += 2

            if score > 0:
                result = row.to_dict()
                result["similarity"] = min(score / 10, 1.0)  # Normalize to 0-1
                matches.append((score, result))

        matches.sort(key=lambda x: -x[0])
        return [m[1] for m in matches[:max_results]]


class SemanticSearcher:
    """Semantic search over product embeddings using ChromaDB."""

    _instance: Optional["SemanticSearcher"] = None

    def __init__(self, index_path: str | Path):
        """Initialize the searcher with a ChromaDB index."""
        import chromadb
        from src.agent.tools.embeddings import EmbeddingService

        self.client = chromadb.PersistentClient(path=str(index_path))
        self.collection = self.client.get_collection("product_embeddings")
        self.embedding_service = EmbeddingService

    @classmethod
    def get_instance(cls, index_path: str | Path | None = None) -> "SemanticSearcher":
        """Get or create a singleton instance."""
        if cls._instance is None:
            from src.agent.tools.vector_index_loader import get_vector_index_path
            if index_path is None:
                index_path = get_vector_index_path()
            cls._instance = cls(index_path)
        return cls._instance

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for products using semantic similarity with hybrid re-ranking."""
        if not query or not query.strip():
            return []

        query_embedding = self.embedding_service.embed_query(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(max_results * 2, 20),
            include=["metadatas", "distances"]
        )

        if not results["ids"][0]:
            return []

        matches = []
        for doc_id, metadata, distance in zip(
            results["ids"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            similarity = 1 - distance
            matches.append({
                "id": doc_id,
                "similarity": similarity,
                **metadata
            })

        return self._hybrid_rerank(query, matches)[:max_results]

    def _hybrid_rerank(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Re-rank results to boost exact keyword matches."""
        query_lower = query.lower()
        query_words = set(query_lower.split())

        for result in results:
            score = result["similarity"]
            product_name = str(result.get("Product Name", "")).lower()
            name_words = set(product_name.split())

            keyword_overlap = len(query_words & name_words)
            score += keyword_overlap * 0.1

            if query_lower in product_name:
                score += 0.2
            elif any(word in product_name for word in query_words):
                score += 0.05

            result["hybrid_score"] = score

        return sorted(results, key=lambda x: -x["hybrid_score"])


def format_product_match(product: Dict[str, Any]) -> str:
    """Format a product match as a human-readable string."""
    name = product.get("Product Name", "Unknown")
    dimensions = product.get("Product Dimensions", "N/A")
    weight = product.get("Shipping Weight", "N/A")
    similarity = product.get("similarity", 0)

    return f"{name}: {dimensions}, {weight} (similarity: {similarity:.2f})"


def lookup_known_product(query: str) -> Dict[str, Any]:
    """Tool function for Claude to look up products.

    Uses semantic search when available, falls back to keyword search.

    Args:
        query: Product search query.

    Returns:
        Dictionary with search results.
    """
    matches = []
    search_method = "keyword"

    # Try semantic search first if enabled
    if SEMANTIC_SEARCH_ENABLED:
        try:
            searcher = SemanticSearcher.get_instance()
            matches = searcher.search(query)
            search_method = "semantic"
        except Exception as e:
            # Log but don't fail - fall back to keyword search
            print(f"Semantic search unavailable, falling back to keyword: {e}")

    # Fall back to keyword search
    if not matches:
        try:
            matches = KeywordSearcher.search(query)
            search_method = "keyword"
        except Exception as e:
            return {
                "found": False,
                "matches": [],
                "best_match": None,
                "message": f"Search error: {str(e)}"
            }

    if not matches:
        return {
            "found": False,
            "matches": [],
            "best_match": None,
            "message": f"No products found matching '{query}'"
        }

    formatted = [format_product_match(m) for m in matches]

    best = matches[0]
    best_match = {
        "product_name": best.get("Product Name"),
        "dimensions": best.get("Product Dimensions"),
        "weight": best.get("Shipping Weight"),
        "category": best.get("Category"),
        "similarity": best.get("similarity"),
    }

    return {
        "found": True,
        "matches": formatted,
        "best_match": best_match,
        "message": f"Found {len(matches)} product(s) matching '{query}' ({search_method} search)"
    }


def _warm_up_semantic_search():
    """Pre-initialize semantic search during Lambda init to reduce cold start latency."""
    if not SEMANTIC_SEARCH_ENABLED:
        return

    try:
        logger.info("Pre-warming semantic search...")
        searcher = SemanticSearcher.get_instance()
        # Run a dummy query to fully initialize the embedding model
        searcher.search("test product", max_results=1)
        logger.info("Semantic search warmed up successfully")
    except Exception as e:
        logger.warning(f"Failed to pre-warm semantic search: {e}")


# Pre-initialize semantic search during module load (Lambda init phase)
# This runs when the container starts, before any requests
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    _warm_up_semantic_search()
