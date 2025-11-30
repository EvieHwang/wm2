"""Feedback retrieval logic for few-shot context injection."""

from typing import List, Dict, Any

from src.feedback.keywords import extract_keywords
from src.feedback.storage import get_recent_feedback, get_feedback_by_keywords


def get_relevant_feedback(description: str, max_entries: int = 15) -> List[Dict[str, Any]]:
    """Retrieve relevant feedback entries for a given description.

    Uses two-tier retrieval:
    1. Recency: Last 10 feedback entries
    2. Keyword: Entries sharing keywords with input

    Results are deduplicated and limited.

    Args:
        description: Product description to find relevant feedback for.
        max_entries: Maximum total entries to return.

    Returns:
        List of relevant feedback items, deduplicated.
    """
    # Tier 1: Get recent feedback
    recent = get_recent_feedback(limit=10)

    # Tier 2: Get keyword-matched feedback
    keywords = extract_keywords(description)
    keyword_matches = get_feedback_by_keywords(keywords, limit=10)

    # Deduplicate by ID, preferring keyword matches (more relevant)
    seen_ids = set()
    result = []

    # Add keyword matches first (higher relevance)
    for item in keyword_matches:
        item_id = item.get("id")
        if item_id not in seen_ids:
            seen_ids.add(item_id)
            result.append(item)

    # Add recent items that weren't already included
    for item in recent:
        item_id = item.get("id")
        if item_id not in seen_ids:
            seen_ids.add(item_id)
            result.append(item)

    return result[:max_entries]


def format_feedback_for_prompt(feedback_items: List[Dict[str, Any]]) -> str:
    """Format feedback items as few-shot context for the classification prompt.

    Args:
        feedback_items: List of feedback items from retrieval.

    Returns:
        Formatted string for prompt injection, or empty string if no items.
    """
    if not feedback_items:
        return ""

    examples = []
    for item in feedback_items:
        desc = item.get("description", "")
        classification = item.get("classification", "")
        is_correct = item.get("is_correct", False)

        # Truncate long descriptions
        if len(desc) > 100:
            desc = desc[:97] + "..."

        if is_correct:
            # Positive example - this classification was correct
            examples.append(
                f"- \"{desc}\" -> {classification} (confirmed correct)"
            )
        else:
            # Negative example - this classification was wrong
            examples.append(
                f"- \"{desc}\" -> {classification} (user indicated incorrect)"
            )

    header = "\n## User Feedback Examples\n\nPrevious classifications with user feedback:\n"
    return header + "\n".join(examples)
