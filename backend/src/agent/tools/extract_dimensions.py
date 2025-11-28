"""Dimension extraction tool for parsing dimensions from text."""

import re
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple


@dataclass
class ParsedDimensions:
    """Structured dimensions extracted from text."""
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    source: str = "explicit"  # "explicit", "reference", "inferred"

    def has_dimensions(self) -> bool:
        """Check if any dimension values are set."""
        return any([self.length, self.width, self.height, self.weight])

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "length": self.length,
            "width": self.width,
            "height": self.height,
            "weight": self.weight,
            "source": self.source,
        }


# Dimension patterns (NxNxN format with optional units)
DIMENSION_PATTERNS = [
    # 10x8x4, 10"x8"x4", 10 x 8 x 4 inches
    r'(\d+(?:\.\d+)?)\s*["\']?\s*[xX×]\s*(\d+(?:\.\d+)?)\s*["\']?\s*[xX×]\s*(\d+(?:\.\d+)?)\s*(?:in(?:ch(?:es)?)?|["\'])?',
    # 10in x 8in x 4in
    r'(\d+(?:\.\d+)?)\s*in(?:ch(?:es)?)?\s*[xX×]\s*(\d+(?:\.\d+)?)\s*in(?:ch(?:es)?)?\s*[xX×]\s*(\d+(?:\.\d+)?)\s*in(?:ch(?:es)?)?',
]

# Single dimension patterns
SINGLE_DIM_PATTERNS = [
    # "about 15 inches", "2 feet long", "6\" tall"
    (r'(\d+(?:\.\d+)?)\s*(?:inches?|in|")', 1.0),           # inches
    (r'(\d+(?:\.\d+)?)\s*(?:feet|foot|ft|\')', 12.0),       # feet to inches
    (r'(\d+(?:\.\d+)?)\s*(?:cm|centimeters?)', 0.3937),     # cm to inches
    (r'(\d+(?:\.\d+)?)\s*(?:mm|millimeters?)', 0.03937),    # mm to inches
]

# Weight patterns with conversion factors to pounds
WEIGHT_PATTERNS = [
    (r'(\d+(?:\.\d+)?)\s*(?:lb(?:s)?|pound(?:s)?)', 1.0),           # pounds
    (r'(\d+(?:\.\d+)?)\s*(?:kg|kilogram(?:s)?|kilo(?:s)?)', 2.205), # kg to lbs
    (r'(\d+(?:\.\d+)?)\s*(?:oz|ounce(?:s)?)', 0.0625),              # oz to lbs
    (r'(\d+(?:\.\d+)?)\s*(?:g|gram(?:s)?)', 0.0022),                # grams to lbs
]


def extract_dimensions_3d(text: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Extract LxWxH dimensions from text.

    Args:
        text: Input text to parse.

    Returns:
        Tuple of (length, width, height) in inches, or (None, None, None).
    """
    text_lower = text.lower()

    for pattern in DIMENSION_PATTERNS:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            try:
                length = float(match.group(1))
                width = float(match.group(2))
                height = float(match.group(3))
                return length, width, height
            except (ValueError, IndexError):
                continue

    return None, None, None


def extract_weight(text: str) -> Optional[float]:
    """Extract weight from text, normalized to pounds.

    Args:
        text: Input text to parse.

    Returns:
        Weight in pounds, or None if not found.
    """
    text_lower = text.lower()

    for pattern, conversion in WEIGHT_PATTERNS:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            try:
                value = float(match.group(1))
                return value * conversion
            except (ValueError, IndexError):
                continue

    return None


def parse_reference_dimensions(dimensions_str: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Parse dimensions from reference data format.

    Reference data uses format like "10 x 8 x 4 inches".

    Args:
        dimensions_str: Dimension string from CSV.

    Returns:
        Tuple of (length, width, height) in inches.
    """
    if not dimensions_str or dimensions_str == "N/A":
        return None, None, None

    return extract_dimensions_3d(dimensions_str)


def parse_reference_weight(weight_str: str) -> Optional[float]:
    """Parse weight from reference data format.

    Reference data uses format like "1.5 pounds".

    Args:
        weight_str: Weight string from CSV.

    Returns:
        Weight in pounds.
    """
    if not weight_str or weight_str == "N/A":
        return None

    return extract_weight(weight_str)


def extract_explicit_dimensions(text: str) -> Dict[str, Any]:
    """Tool function for Claude to extract dimensions from user input.

    This is the main entry point called by the agent.

    Args:
        text: User's product description text.

    Returns:
        Dictionary with extraction results:
        - found: bool - Whether any dimensions were extracted
        - dimensions: ParsedDimensions dict
        - summary: Human-readable summary
    """
    length, width, height = extract_dimensions_3d(text)
    weight = extract_weight(text)

    dims = ParsedDimensions(
        length=length,
        width=width,
        height=height,
        weight=weight,
        source="explicit"
    )

    if not dims.has_dimensions():
        return {
            "found": False,
            "dimensions": dims.to_dict(),
            "summary": "No explicit dimensions found in input"
        }

    # Build summary
    parts = []
    if length and width and height:
        parts.append(f"{length}×{width}×{height} in")
    if weight:
        parts.append(f"{weight:.2f} lbs")

    summary = ", ".join(parts) if parts else "Partial dimensions found"

    return {
        "found": True,
        "dimensions": dims.to_dict(),
        "summary": summary
    }
