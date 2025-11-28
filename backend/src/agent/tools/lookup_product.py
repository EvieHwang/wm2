"""Product lookup tool for searching reference database."""

from typing import List, Dict, Any, Optional

import pandas as pd

from src.data.reference_loader import get_reference_data


def search_reference_data(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search reference CSV for products matching the query.

    Performs case-insensitive keyword matching against:
    - Product Name
    - Category
    - About Product

    Args:
        query: Search query string.
        max_results: Maximum number of matches to return.

    Returns:
        List of matching product dictionaries, sorted by relevance score.
    """
    if not query or not query.strip():
        return []

    df = get_reference_data()
    query_lower = query.lower()
    keywords = query_lower.split()

    matches = []
    for idx, row in df.iterrows():
        # Build searchable text from key fields
        searchable_parts = [
            str(row.get("Product Name", "")),
            str(row.get("Category", "")),
            str(row.get("About Product", "")),
        ]
        searchable = " ".join(searchable_parts).lower()

        # Score by number of keyword matches
        score = sum(1 for kw in keywords if kw in searchable)

        # Bonus for exact product name match
        product_name = str(row.get("Product Name", "")).lower()
        if query_lower in product_name:
            score += 5
        elif any(kw in product_name for kw in keywords):
            score += 2

        if score > 0:
            matches.append((score, row.to_dict()))

    # Sort by score descending, return top matches
    matches.sort(key=lambda x: -x[0])
    return [m[1] for m in matches[:max_results]]


def format_product_match(product: Dict[str, Any]) -> str:
    """Format a product match as a human-readable string.

    Args:
        product: Product dictionary from reference data.

    Returns:
        Formatted string with product details.
    """
    name = product.get("Product Name", "Unknown")
    dimensions = product.get("Product Dimensions", "N/A")
    weight = product.get("Shipping Weight", "N/A")

    return f"{name}: {dimensions}, {weight}"


def lookup_known_product(query: str) -> Dict[str, Any]:
    """Tool function for Claude to look up products.

    This is the main entry point called by the agent.

    Args:
        query: Product search query.

    Returns:
        Dictionary with search results:
        - found: bool - Whether any matches were found
        - matches: List of formatted match strings
        - best_match: Optional dict with dimensions/weight if found
    """
    matches = search_reference_data(query)

    if not matches:
        return {
            "found": False,
            "matches": [],
            "best_match": None,
            "message": f"No products found matching '{query}'"
        }

    # Format matches for display
    formatted = [format_product_match(m) for m in matches]

    # Extract dimensions from best match
    best = matches[0]
    best_match = {
        "product_name": best.get("Product Name"),
        "dimensions": best.get("Product Dimensions"),
        "weight": best.get("Shipping Weight"),
        "category": best.get("Category"),
    }

    return {
        "found": True,
        "matches": formatted,
        "best_match": best_match,
        "message": f"Found {len(matches)} product(s) matching '{query}'"
    }
