"""Main agent classifier using Claude API with tool use."""

import json
import logging
import os
import re
from typing import Any, Dict, Optional

from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError, APITimeoutError

# Configure logging
logger = logging.getLogger(__name__)

from src.agent.prompts import TOOLS, SYSTEM_PROMPT, get_classification_prompt, get_feedback_context
from src.feedback.retrieval import get_relevant_feedback
from src.agent.tools.lookup_product import lookup_known_product
from src.agent.tools.extract_dimensions import extract_explicit_dimensions, parse_reference_dimensions, parse_reference_weight
from src.models.categories import CategoryEnum, classify_by_dimensions
from src.models.response import (
    ClassificationResult,
    ToolUsageRecord,
    ToolInvocation,
)


# Tool dispatch mapping
TOOL_HANDLERS = {
    "lookup_known_product": lambda args: lookup_known_product(args.get("query", "")),
    "extract_explicit_dimensions": lambda args: extract_explicit_dimensions(args.get("text", "")),
}


def get_anthropic_client() -> Anthropic:
    """Get Anthropic client with API key from environment."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    return Anthropic(api_key=api_key)


def process_tool_call(tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool call and return the result.

    Args:
        tool_name: Name of the tool to call.
        tool_input: Input arguments for the tool.

    Returns:
        Tool result dictionary.
    """
    handler = TOOL_HANDLERS.get(tool_name)
    if not handler:
        return {"error": f"Unknown tool: {tool_name}"}

    try:
        return handler(tool_input)
    except Exception as e:
        return {"error": str(e)}


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON object from text response.

    Args:
        text: Text that may contain a JSON object.

    Returns:
        Parsed JSON dict or None if not found.
    """
    # Try to find JSON block in the text
    json_patterns = [
        r'<result>\s*(.*?)\s*</result>',  # XML-style result tags
        r'```json\s*(.*?)\s*```',  # Markdown code block
        r'```\s*(.*?)\s*```',       # Generic code block
    ]

    for pattern in json_patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                json_str = match.group(1)
                return json.loads(json_str)
            except json.JSONDecodeError:
                continue

    # Try to find a JSON object with classification key anywhere in text
    json_obj_pattern = r'\{[^{}]*"classification"[^{}]*\}'
    match = re.search(json_obj_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Try parsing the entire text as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


class ClassificationError(Exception):
    """Custom exception for classification errors."""
    pass


def classify_product(description: str) -> ClassificationResult:
    """Classify a product using Claude with tool use.

    Args:
        description: Product description to classify.

    Returns:
        ClassificationResult with classification, confidence, reasoning, and tool usage.

    Raises:
        ClassificationError: If classification fails due to API errors.
    """
    try:
        client = get_anthropic_client()
    except ValueError as e:
        logger.error(f"Failed to initialize Anthropic client: {e}")
        raise ClassificationError("Service configuration error") from e

    tools_used = ToolUsageRecord()

    # Retrieve relevant feedback for few-shot context
    feedback_items = get_relevant_feedback(description)
    feedback_context = get_feedback_context(feedback_items)

    # Build system prompt with feedback context
    system_prompt = SYSTEM_PROMPT
    if feedback_context:
        system_prompt = SYSTEM_PROMPT + "\n" + feedback_context

    # Initial message to Claude
    messages = [
        {"role": "user", "content": get_classification_prompt(description)}
    ]

    # Track tool results for building reasoning
    tool_results = {}

    # Agentic loop - keep processing until we get a final response
    max_iterations = 5
    response = None

    for iteration in range(max_iterations):
        try:
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                system=system_prompt,
                tools=TOOLS,
                tool_choice={"type": "auto"},
                messages=messages,
                timeout=25.0,  # 25 second timeout (Lambda has 30s)
            )
        except APITimeoutError as e:
            logger.error(f"Claude API timeout on iteration {iteration}: {e}")
            raise ClassificationError("Request timed out. Please try again.") from e
        except RateLimitError as e:
            logger.error(f"Claude API rate limit exceeded: {e}")
            raise ClassificationError("Service is busy. Please try again in a moment.") from e
        except APIConnectionError as e:
            logger.error(f"Claude API connection error: {e}")
            raise ClassificationError("Unable to connect to classification service.") from e
        except APIError as e:
            logger.error(f"Claude API error: {e}")
            raise ClassificationError("Classification service error. Please try again.") from e

        # Check if Claude wants to use tools
        if response.stop_reason == "tool_use":
            # Process each tool use in the response
            tool_use_blocks = [
                block for block in response.content
                if block.type == "tool_use"
            ]

            tool_results_for_message = []
            for tool_use in tool_use_blocks:
                tool_name = tool_use.name
                tool_input = tool_use.input

                # Execute the tool
                result = process_tool_call(tool_name, tool_input)
                tool_results[tool_name] = result

                # Track tool usage
                if tool_name == "lookup_known_product":
                    tools_used.lookup_known_product = ToolInvocation(
                        called=True,
                        result=result.get("message", str(result)),
                    )
                elif tool_name == "extract_explicit_dimensions":
                    tools_used.extract_explicit_dimensions = ToolInvocation(
                        called=True,
                        result=result.get("summary", str(result)),
                    )

                tool_results_for_message.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result),
                })

            # Add assistant response and tool results to messages
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results_for_message})

        else:
            # Claude has finished - extract the final response
            break

    # Set reasons for tools not called
    if not tools_used.lookup_known_product.called:
        tools_used.lookup_known_product = ToolInvocation(
            called=False,
            reason="Agent did not need product lookup"
        )
    if not tools_used.extract_explicit_dimensions.called:
        tools_used.extract_explicit_dimensions = ToolInvocation(
            called=False,
            reason="No explicit dimensions in input"
        )

    # Extract text response
    text_content = ""
    for block in response.content:
        if hasattr(block, "text"):
            text_content += block.text

    # Parse the JSON response from Claude
    parsed = extract_json_from_text(text_content)

    if parsed:
        # Use Claude's classification
        classification_str = parsed.get("classification", "TOTE")
        try:
            classification = CategoryEnum(classification_str)
        except ValueError:
            classification = CategoryEnum.TOTE

        confidence = int(parsed.get("confidence", 70))
        reasoning = parsed.get("reasoning", text_content)
    else:
        # Fallback: try to determine classification from tool results
        classification = CategoryEnum.TOTE
        confidence = 50
        reasoning = text_content or "Unable to parse classification response"

        # If we have dimensions from tools, use them
        if "extract_explicit_dimensions" in tool_results:
            dims = tool_results["extract_explicit_dimensions"].get("dimensions", {})
            if dims:
                classification = classify_by_dimensions(
                    dims.get("length"),
                    dims.get("width"),
                    dims.get("height"),
                    dims.get("weight"),
                )
                confidence = 85

        elif "lookup_known_product" in tool_results:
            lookup_result = tool_results["lookup_known_product"]
            if lookup_result.get("found") and lookup_result.get("best_match"):
                best = lookup_result["best_match"]
                dims = parse_reference_dimensions(best.get("dimensions", ""))
                weight = parse_reference_weight(best.get("weight", ""))
                classification = classify_by_dimensions(
                    dims[0], dims[1], dims[2], weight
                )
                confidence = 80

    return ClassificationResult(
        classification=classification,
        confidence=min(100, max(0, confidence)),  # Clamp to 0-100
        reasoning=reasoning,
        tools_used=tools_used,
    )
