"""Category definitions and constraints for ASRS classification."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CategoryEnum(str, Enum):
    """Container categories for ASRS routing."""
    POUCH = "POUCH"
    SMALL_BIN = "SMALL_BIN"
    TOTE = "TOTE"
    CARTON = "CARTON"
    OVERSIZED = "OVERSIZED"


@dataclass(frozen=True)
class CategoryConstraints:
    """Dimensional and weight limits for a category."""
    category: CategoryEnum
    max_length: float  # inches
    max_width: float   # inches
    max_height: float  # inches
    max_weight: float  # pounds

    def fits(self, length: Optional[float], width: Optional[float],
             height: Optional[float], weight: Optional[float]) -> bool:
        """Check if dimensions/weight fit within category constraints.

        None values are treated as fitting (unknown dimensions don't disqualify).
        """
        if self.category == CategoryEnum.OVERSIZED:
            return True

        if length is not None and length > self.max_length:
            return False
        if width is not None and width > self.max_width:
            return False
        if height is not None and height > self.max_height:
            return False
        if weight is not None and weight > self.max_weight:
            return False
        return True


# Category constraints ordered from smallest to largest
CATEGORY_CONSTRAINTS = [
    CategoryConstraints(CategoryEnum.POUCH, 12.0, 9.0, 2.0, 1.0),
    CategoryConstraints(CategoryEnum.SMALL_BIN, 12.0, 9.0, 6.0, 10.0),
    CategoryConstraints(CategoryEnum.TOTE, 18.0, 14.0, 12.0, 50.0),
    CategoryConstraints(CategoryEnum.CARTON, 24.0, 18.0, 18.0, 70.0),
    CategoryConstraints(CategoryEnum.OVERSIZED, float('inf'), float('inf'), float('inf'), float('inf')),
]


def classify_by_dimensions(
    length: Optional[float] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    weight: Optional[float] = None
) -> CategoryEnum:
    """Determine the smallest category that fits the given dimensions.

    Returns the smallest category where all provided dimensions fit.
    Unknown dimensions (None) do not disqualify a category.
    """
    for constraint in CATEGORY_CONSTRAINTS:
        if constraint.fits(length, width, height, weight):
            return constraint.category
    return CategoryEnum.OVERSIZED


def get_category_display_name(category: CategoryEnum) -> str:
    """Get human-readable display name for a category."""
    display_names = {
        CategoryEnum.POUCH: "Pouch",
        CategoryEnum.SMALL_BIN: "Small Bin",
        CategoryEnum.TOTE: "Tote",
        CategoryEnum.CARTON: "Carton",
        CategoryEnum.OVERSIZED: "Oversized",
    }
    return display_names.get(category, category.value)


def get_category_description(category: CategoryEnum) -> str:
    """Get description of typical products for a category."""
    descriptions = {
        CategoryEnum.POUCH: "Apparel, soft goods, flat items",
        CategoryEnum.SMALL_BIN: "Electronics, small parts, cosmetics",
        CategoryEnum.TOTE: "General merchandise, packaged goods",
        CategoryEnum.CARTON: "Bulky items, multi-packs",
        CategoryEnum.OVERSIZED: "Items exceeding standard container limits",
    }
    return descriptions.get(category, "")
