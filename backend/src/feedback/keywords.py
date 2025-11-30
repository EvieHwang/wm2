"""Keyword extraction utility for feedback matching."""

import re
from typing import List, Set

# Common English stopwords to filter out
STOPWORDS: Set[str] = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "up", "about", "into", "over", "after",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "must", "shall", "can", "need", "dare", "ought", "used", "it", "its",
    "this", "that", "these", "those", "i", "you", "he", "she", "we", "they",
    "what", "which", "who", "whom", "when", "where", "why", "how", "all",
    "each", "every", "both", "few", "more", "most", "other", "some", "such",
    "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "just", "also", "now", "here", "there", "then", "once", "any", "if",
    "product", "item", "box", "package", "description", "approximately",
    "approx", "about", "around", "roughly", "exactly", "please", "thanks",
}

# Minimum keyword length
MIN_KEYWORD_LENGTH = 3


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric words.

    Args:
        text: Input text to tokenize.

    Returns:
        List of lowercase tokens.
    """
    # Convert to lowercase and extract alphanumeric sequences
    tokens = re.findall(r'[a-z0-9]+', text.lower())
    return tokens


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract meaningful keywords from text.

    Applies stopword filtering and minimum length requirements.

    Args:
        text: Input text to extract keywords from.
        max_keywords: Maximum number of keywords to return.

    Returns:
        List of extracted keywords, deduplicated and limited.
    """
    if not text:
        return []

    tokens = tokenize(text)

    # Filter stopwords and short tokens
    keywords = [
        token for token in tokens
        if token not in STOPWORDS and len(token) >= MIN_KEYWORD_LENGTH
    ]

    # Deduplicate while preserving order
    seen = set()
    unique_keywords = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)

    return unique_keywords[:max_keywords]
