"""Lambda handler for ASRS Storage Classifier API."""

import json
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from src.models.response import ClassificationRequest, ErrorResponse
from src.agent.classifier import classify_product, ClassificationError
from src.feedback.storage import store_feedback


def validate_classification_request(body: Dict[str, Any]) -> Tuple[Optional[ClassificationRequest], Optional[ErrorResponse]]:
    """Validate and parse classification request body.

    Args:
        body: Parsed JSON request body.

    Returns:
        Tuple of (request, error). One will always be None.
        - If valid: (ClassificationRequest, None)
        - If invalid: (None, ErrorResponse)
    """
    # Check for description field
    if "description" not in body:
        return None, ErrorResponse(
            error="validation_error",
            message="Missing required field: description"
        )

    description = body.get("description")

    # Check for empty/whitespace
    if not description or not str(description).strip():
        return None, ErrorResponse(
            error="validation_error",
            message="Please enter a product description"
        )

    # Convert to string and check length
    description_str = str(description).strip()
    if len(description_str) > 2000:
        return None, ErrorResponse(
            error="validation_error",
            message="Description must not exceed 2000 characters"
        )

    try:
        request = ClassificationRequest(description=description_str)
        return request, None
    except ValueError as e:
        return None, ErrorResponse(
            error="validation_error",
            message=str(e)
        )


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Create API Gateway response with CORS headers."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
        },
        "body": json.dumps(body),
    }


def handle_health(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle GET /health endpoint."""
    return create_response(200, {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })


def validate_feedback_request(body: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[ErrorResponse]]:
    """Validate feedback request body.

    Args:
        body: Parsed JSON request body.

    Returns:
        Tuple of (validated_data, error). One will always be None.
    """
    # Check required fields
    required_fields = ["description", "classification", "is_correct"]
    for field in required_fields:
        if field not in body:
            return None, ErrorResponse(
                error="validation_error",
                message=f"Missing required field: {field}"
            )

    description = body.get("description", "")
    classification = body.get("classification", "")
    is_correct = body.get("is_correct")

    # Validate description
    if not description or not str(description).strip():
        return None, ErrorResponse(
            error="validation_error",
            message="Description cannot be empty"
        )

    # Validate classification
    valid_classifications = ["POUCH", "SMALL_BIN", "TOTE", "CARTON", "OVERSIZED"]
    if classification not in valid_classifications:
        return None, ErrorResponse(
            error="validation_error",
            message=f"Invalid classification. Must be one of: {', '.join(valid_classifications)}"
        )

    # Validate is_correct is boolean
    if not isinstance(is_correct, bool):
        return None, ErrorResponse(
            error="validation_error",
            message="is_correct must be a boolean"
        )

    return {
        "description": str(description).strip(),
        "classification": classification,
        "is_correct": is_correct,
    }, None


def handle_feedback(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle POST /v1/feedback endpoint."""
    # Parse request body
    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return create_response(400, ErrorResponse(
            error="validation_error",
            message="Invalid JSON in request body"
        ).to_dict())

    # Validate request
    validated, error = validate_feedback_request(body)
    if error:
        return create_response(400, error.to_dict())

    # Store feedback
    result = store_feedback(
        description=validated["description"],
        classification=validated["classification"],
        is_correct=validated["is_correct"],
    )

    if result is None:
        return create_response(500, ErrorResponse(
            error="service_error",
            message="Failed to store feedback"
        ).to_dict())

    return create_response(200, {
        "success": True,
        "id": result.get("id"),
        "message": "Feedback recorded successfully"
    })


def handle_classify(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle POST /classify endpoint."""
    # Parse request body
    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return create_response(400, ErrorResponse(
            error="validation_error",
            message="Invalid JSON in request body"
        ).to_dict())

    # Validate request
    request, error = validate_classification_request(body)
    if error:
        return create_response(400, error.to_dict())

    # Call classifier and return result
    try:
        result = classify_product(request.description)
        return create_response(200, result.to_dict())
    except ClassificationError as e:
        # Handle known classification errors with specific messages
        return create_response(500, ErrorResponse(
            error="service_error",
            message=str(e)
        ).to_dict())
    except Exception as e:
        # Handle unexpected errors gracefully
        return create_response(500, ErrorResponse(
            error="service_error",
            message="Service temporarily unavailable. Please try again."
        ).to_dict())


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda entry point.

    Routes requests to appropriate handlers based on HTTP method and path.
    """
    http_method = event.get("httpMethod", "GET")
    path = event.get("path", "/")

    # Route to appropriate handler
    if path == "/health" and http_method == "GET":
        return handle_health(event)
    elif path == "/classify" and http_method == "POST":
        return handle_classify(event)
    elif path == "/v1/feedback" and http_method == "POST":
        return handle_feedback(event)
    elif http_method == "OPTIONS":
        # CORS preflight
        return create_response(200, {})
    else:
        return create_response(404, ErrorResponse(
            error="not_found",
            message=f"Unknown endpoint: {http_method} {path}"
        ).to_dict())
