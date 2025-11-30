"""DynamoDB storage for feedback entries."""

import os
import uuid
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import boto3
from boto3.dynamodb.conditions import Key

from src.feedback.keywords import extract_keywords

logger = logging.getLogger(__name__)

# Module-level DynamoDB resource (reused across invocations)
_dynamodb_resource = None
_feedback_table = None


def get_dynamodb_resource():
    """Get or create DynamoDB resource."""
    global _dynamodb_resource
    if _dynamodb_resource is None:
        _dynamodb_resource = boto3.resource("dynamodb")
    return _dynamodb_resource


def get_feedback_table():
    """Get DynamoDB feedback table.

    Returns:
        DynamoDB Table resource or None if table name not configured.
    """
    global _feedback_table
    if _feedback_table is None:
        table_name = os.environ.get("FEEDBACK_TABLE_NAME")
        if not table_name:
            logger.warning("FEEDBACK_TABLE_NAME not set, feedback disabled")
            return None
        _feedback_table = get_dynamodb_resource().Table(table_name)
    return _feedback_table


def store_feedback(
    description: str,
    classification: str,
    is_correct: bool,
) -> Optional[Dict[str, Any]]:
    """Store a feedback entry in DynamoDB.

    Args:
        description: Original product description.
        classification: The predicted classification.
        is_correct: Whether the user marked this as correct (thumbs up).

    Returns:
        The stored feedback item, or None if storage failed.
    """
    table = get_feedback_table()
    if table is None:
        return None

    # Extract keywords for future matching
    keywords = extract_keywords(description)

    # Generate unique ID and timestamp
    feedback_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + "Z"

    item = {
        "id": feedback_id,
        "timestamp": timestamp,
        "description": description,
        "classification": classification,
        "is_correct": is_correct,
        "keywords": keywords,
    }

    try:
        table.put_item(Item=item)
        logger.info(f"Stored feedback {feedback_id}: {classification}, correct={is_correct}")
        return item
    except Exception as e:
        logger.error(f"Failed to store feedback: {e}")
        return None


def get_recent_feedback(limit: int = 10) -> list:
    """Get the most recent feedback entries.

    Args:
        limit: Maximum number of entries to return.

    Returns:
        List of feedback items, most recent first.
    """
    table = get_feedback_table()
    if table is None:
        return []

    try:
        # Scan and sort by timestamp (for small datasets this is acceptable)
        # For larger scale, consider a GSI on timestamp
        response = table.scan(Limit=limit * 2)  # Get extra to allow for sorting
        items = response.get("Items", [])

        # Sort by timestamp descending
        items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return items[:limit]
    except Exception as e:
        logger.error(f"Failed to get recent feedback: {e}")
        return []


def get_feedback_by_keywords(keywords: list, limit: int = 10) -> list:
    """Get feedback entries matching any of the given keywords.

    Args:
        keywords: List of keywords to match.
        limit: Maximum number of entries to return.

    Returns:
        List of feedback items with matching keywords.
    """
    table = get_feedback_table()
    if table is None or not keywords:
        return []

    try:
        # Scan for entries with overlapping keywords
        # For production scale, consider using a separate keywords index
        response = table.scan()
        items = response.get("Items", [])

        # Score items by keyword overlap
        keyword_set = set(keywords)
        scored_items = []
        for item in items:
            item_keywords = set(item.get("keywords", []))
            overlap = len(keyword_set & item_keywords)
            if overlap > 0:
                scored_items.append((overlap, item))

        # Sort by overlap score descending, then by timestamp
        scored_items.sort(
            key=lambda x: (x[0], x[1].get("timestamp", "")),
            reverse=True
        )

        return [item for _, item in scored_items[:limit]]
    except Exception as e:
        logger.error(f"Failed to get keyword feedback: {e}")
        return []
