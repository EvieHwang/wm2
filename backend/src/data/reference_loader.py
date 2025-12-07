"""Reference data loader for product lookup with S3 support."""

import os
from io import StringIO
from pathlib import Path
from typing import Optional

import boto3
import pandas as pd


# Module-level cache for reference data
_reference_df: Optional[pd.DataFrame] = None

# S3 configuration
REFERENCE_DATA_BUCKET = os.environ.get("REFERENCE_DATA_BUCKET", "wm2-asrs-classifier-frontend")
REFERENCE_DATA_KEY = os.environ.get("REFERENCE_DATA_KEY", "data/wm_weight_and_dim.csv")


def get_reference_data_path() -> Optional[Path]:
    """Get the path to the local reference CSV file.

    Returns:
        Path to the CSV file, or None if not found locally.
    """
    # Check for environment variable first
    env_path = os.environ.get("REFERENCE_DATA_PATH")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path

    # Search for local file in development
    current = Path(__file__).resolve()
    for _ in range(5):
        data_path = current.parent / "data" / "wm_weight_and_dim.csv"
        if data_path.exists():
            return data_path
        current = current.parent

    # Try standard project structure
    fallback = Path(__file__).resolve().parents[3] / "data" / "wm_weight_and_dim.csv"
    if fallback.exists():
        return fallback

    return None


def load_from_s3() -> pd.DataFrame:
    """Load reference data from S3.

    Returns:
        DataFrame with product reference data.

    Raises:
        Exception: If S3 download fails.
    """
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=REFERENCE_DATA_BUCKET, Key=REFERENCE_DATA_KEY)
    csv_content = response["Body"].read().decode("utf-8")
    return pd.read_csv(StringIO(csv_content))


def load_reference_data(force_reload: bool = False) -> pd.DataFrame:
    """Load the reference CSV into memory.

    Tries local file first, falls back to S3 in Lambda environment.
    Uses module-level caching to avoid reloading on each invocation.

    Args:
        force_reload: If True, bypass cache and reload.

    Returns:
        DataFrame with product reference data.

    Raises:
        FileNotFoundError: If data cannot be found locally or in S3.
    """
    global _reference_df

    if _reference_df is not None and not force_reload:
        return _reference_df

    # Try local file first
    local_path = get_reference_data_path()
    if local_path:
        _reference_df = pd.read_csv(local_path)
        return _reference_df

    # Fall back to S3 (Lambda environment)
    try:
        print(f"Loading reference data from s3://{REFERENCE_DATA_BUCKET}/{REFERENCE_DATA_KEY}")
        _reference_df = load_from_s3()
        return _reference_df
    except Exception as e:
        raise FileNotFoundError(
            f"Reference data not found locally or in S3: {e}"
        ) from e


def get_reference_data() -> pd.DataFrame:
    """Get the cached reference data, loading if necessary."""
    return load_reference_data()


def get_product_count() -> int:
    """Get the number of products in the reference data."""
    return len(get_reference_data())
