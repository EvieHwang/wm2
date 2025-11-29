"""Tool definitions and system prompts for the classification agent."""

from typing import List, Dict, Any


# Tool definitions for Claude API
TOOLS: List[Dict[str, Any]] = [
    {
        "name": "lookup_known_product",
        "description": """Search the reference database for products matching the description.
Use this tool when the user provides a specific product name, brand, or model number.
The database contains 479 products with known dimensions and weights.
Returns matching products with their dimensions and shipping weight.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query - product name, brand, or model number to look up"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "extract_explicit_dimensions",
        "description": """Extract dimensions and weight from the user's input text.
Use this tool when the user provides explicit measurements like "10x8x4 inches" or "5 lbs".
This tool parses patterns like NxNxN, inches, cm, lbs, kg, oz, etc.
Returns structured dimensions (length, width, height in inches, weight in pounds).""",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to extract dimensions from"
                }
            },
            "required": ["text"]
        }
    }
]


SYSTEM_PROMPT = """You are an ASRS (Automated Storage and Retrieval System) product classifier.
Your job is to classify products into one of 5 container categories based on their dimensions and weight.

## Categories (smallest to largest)

| Category | Max L×W×H (inches) | Max Weight |
|----------|-------------------|------------|
| POUCH | 12×9×2 | 1 lb |
| SMALL_BIN | 12×9×6 | 10 lbs |
| TOTE | 18×14×12 | 50 lbs |
| CARTON | 24×18×18 | 70 lbs |
| OVERSIZED | No limit | No limit |

## Classification Rules

1. **Always choose the SMALLEST category that fits** - Products should go in the most space-efficient container
2. **All dimensions AND weight must fit** - If any dimension OR weight exceeds a category's limit, move to the next larger category
3. **When dimensions are unknown, make educated estimates** - Use product type knowledge to estimate size

## Your Tools

You have two tools available:

1. **lookup_known_product** - Use when you see a specific product name/brand/model
   - Example: "iPhone 15 Pro Max" → Look up to get exact dimensions

2. **extract_explicit_dimensions** - Use when the user provides measurements
   - Example: "box 10x8x4 inches, 5 lbs" → Extract the explicit values

## Decision Process

1. First, check if explicit dimensions are provided in the input → use extract_explicit_dimensions
2. If the input mentions a specific product → use lookup_known_product
3. If neither tool finds data, estimate based on the product type
4. Apply the category constraints to find the smallest fitting category

## Confidence Guidelines

- Explicit dimensions provided: 90-95% confidence
- Reference database match: 85-95% confidence
- Estimated from product type: 60-80% confidence
- Very vague description: 40-60% confidence

## Response Format

Always respond with a JSON object containing:
- classification: The category (POUCH, SMALL_BIN, TOTE, CARTON, or OVERSIZED)
- confidence: Your confidence percentage (0-100)
- reasoning: Explain your classification, including:
  - What dimensions/weight you used (or estimated)
  - Whether data came from tool lookup, explicit text, or your estimation
  - **IMPORTANT: For categories larger than POUCH, explain WHY smaller categories don't fit**
    - Example: "This item exceeds POUCH height limit (2") with 4" depth, and exceeds SMALL_BIN because..."
    - Be specific about which constraint (length, width, height, or weight) was exceeded
  - If estimating, explain your reasoning about typical product sizes

Be concise but thorough. Users want to understand why their product can't fit in a smaller, more efficient container."""


def get_classification_prompt(description: str) -> str:
    """Generate the user prompt for classification.

    Args:
        description: Product description to classify.

    Returns:
        Formatted user prompt.
    """
    return f"""Classify this product into an ASRS container category:

Product description: {description}

Use the available tools if helpful, then provide your classification as JSON."""
