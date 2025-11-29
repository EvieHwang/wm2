"""Reference data loader for product lookup."""

import os
from pathlib import Path
from typing import Optional

import pandas as pd


# Module-level cache for reference data
_reference_df: Optional[pd.DataFrame] = None


def get_reference_data_path() -> Path:
    """Get the path to the reference CSV file."""
    # Check for environment variable first (for Lambda deployment)
    env_path = os.environ.get("REFERENCE_DATA_PATH")
    if env_path:
        return Path(env_path)

    # Default to local data directory (relative to project root)
    # Walk up from this file to find the data directory
    current = Path(__file__).resolve()
    for _ in range(5):  # Max depth to search
        data_path = current.parent / "data" / "wm_weight_and_dim.csv"
        if data_path.exists():
            return data_path
        current = current.parent

    # Fallback: assume standard project structure
    return Path(__file__).resolve().parents[3] / "data" / "wm_weight_and_dim.csv"


def load_reference_data(force_reload: bool = False) -> pd.DataFrame:
    """Load the reference CSV into memory.

    Uses module-level caching to avoid reloading on each Lambda invocation.

    Args:
        force_reload: If True, bypass cache and reload from disk.

    Returns:
        DataFrame with product reference data.

    Raises:
        FileNotFoundError: If the CSV file doesn't exist.
    """
    global _reference_df

    if _reference_df is not None and not force_reload:
        return _reference_df

    csv_path = get_reference_data_path()
    if not csv_path.exists():
        raise FileNotFoundError(f"Reference data not found at {csv_path}")

    _reference_df = pd.read_csv(csv_path)
    return _reference_df


def get_reference_data() -> pd.DataFrame:
    """Get the cached reference data, loading if necessary."""
    return load_reference_data()


def get_product_count() -> int:
    """Get the number of products in the reference data."""
    return len(get_reference_data())
