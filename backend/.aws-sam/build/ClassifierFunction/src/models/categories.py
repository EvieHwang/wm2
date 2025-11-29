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


def get_rejection_reasons(
    length: Optional[float] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    weight: Optional[float] = None
) -> dict[CategoryEnum, str]:
    """Get reasons why each smaller category was rejected.

    Useful for generating reasoning in classification results.

    Returns:
        Dictionary mapping rejected categories to explanation strings.
    """
    reasons = {}
    final_category = classify_by_dimensions(length, width, height, weight)

    for constraint in CATEGORY_CONSTRAINTS:
        if constraint.category == final_category:
            break  # Stop at the final category

        # Check which constraint was exceeded
        exceeded = []
        if length is not None and length > constraint.max_length:
            exceeded.append(f"length {length}\" > {constraint.max_length}\"")
        if width is not None and width > constraint.max_width:
            exceeded.append(f"width {width}\" > {constraint.max_width}\"")
        if height is not None and height > constraint.max_height:
            exceeded.append(f"height {height}\" > {constraint.max_height}\"")
        if weight is not None and weight > constraint.max_weight:
            exceeded.append(f"weight {weight} lbs > {constraint.max_weight} lbs")

        if exceeded:
            reasons[constraint.category] = f"Exceeds {get_category_display_name(constraint.category)}: {', '.join(exceeded)}"

    return reasons


def get_category_constraints_dict(category: CategoryEnum) -> dict:
    """Get constraints for a category as a dictionary."""
    for constraint in CATEGORY_CONSTRAINTS:
        if constraint.category == category:
            return {
                "max_length": constraint.max_length,
                "max_width": constraint.max_width,
                "max_height": constraint.max_height,
                "max_weight": constraint.max_weight,
            }
    return {}
