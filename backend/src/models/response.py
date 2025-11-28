"""Response models for classification API."""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any

from .categories import CategoryEnum


@dataclass
class ToolInvocation:
    """Details about a single tool's usage."""
    called: bool
    result: Optional[str] = None
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        d = {"called": self.called}
        if self.result is not None:
            d["result"] = self.result
        if self.reason is not None:
            d["reason"] = self.reason
        return d


@dataclass
class ToolUsageRecord:
    """Records which agent tools were called during classification."""
    lookup_known_product: ToolInvocation = field(
        default_factory=lambda: ToolInvocation(called=False)
    )
    extract_explicit_dimensions: ToolInvocation = field(
        default_factory=lambda: ToolInvocation(called=False)
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "lookup_known_product": self.lookup_known_product.to_dict(),
            "extract_explicit_dimensions": self.extract_explicit_dimensions.to_dict(),
        }


@dataclass
class ClassificationResult:
    """The output of a classification request."""
    classification: CategoryEnum
    confidence: int  # 0-100
    reasoning: str
    tools_used: ToolUsageRecord = field(default_factory=ToolUsageRecord)

    def __post_init__(self):
        """Validate confidence is within bounds."""
        if not 0 <= self.confidence <= 100:
            raise ValueError(f"Confidence must be 0-100, got {self.confidence}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        return {
            "classification": self.classification.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "tools_used": self.tools_used.to_dict(),
        }


@dataclass
class ClassificationRequest:
    """The input from a user requesting product classification."""
    description: str

    def __post_init__(self):
        """Validate description."""
        if not self.description or not self.description.strip():
            raise ValueError("Description must not be empty")
        if len(self.description) > 2000:
            raise ValueError("Description must not exceed 2000 characters")


@dataclass
class ErrorResponse:
    """Error response structure."""
    error: str
    message: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        return {
            "error": self.error,
            "message": self.message,
        }
