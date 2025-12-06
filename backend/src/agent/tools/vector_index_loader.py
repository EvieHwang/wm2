"""Vector index loader with S3 support for Lambda deployment."""

import os
import shutil
from pathlib import Path
from typing import Optional

import boto3
from botocore.exceptions import ClientError


# S3 configuration from environment
VECTOR_INDEX_BUCKET = os.environ.get("VECTOR_INDEX_BUCKET", "wm2-asrs-classifier-frontend")
VECTOR_INDEX_PREFIX = os.environ.get("VECTOR_INDEX_PREFIX", "vector_index/")

# Local paths
LOCAL_INDEX_PATH = Path("/tmp/vector_index")
DEFAULT_DEV_PATH = Path(__file__).parent.parent.parent.parent / "data" / "vector_index"


def download_from_s3(bucket: str, prefix: str, local_path: Path) -> bool:
    """Download vector index directory from S3.

    Args:
        bucket: S3 bucket name.
        prefix: S3 prefix (folder path).
        local_path: Local directory to download to.

    Returns:
        True if successful, False otherwise.
    """
    s3 = boto3.client("s3")

    try:
        # List all objects under the prefix
        paginator = s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

        local_path.mkdir(parents=True, exist_ok=True)
        downloaded = 0

        for page in pages:
            for obj in page.get("Contents", []):
                key = obj["Key"]
                # Skip the prefix itself
                if key == prefix:
                    continue

                # Calculate relative path
                relative = key[len(prefix):]
                if not relative:
                    continue

                local_file = local_path / relative
                local_file.parent.mkdir(parents=True, exist_ok=True)

                s3.download_file(bucket, key, str(local_file))
                downloaded += 1

        print(f"Downloaded {downloaded} files from s3://{bucket}/{prefix}")
        return downloaded > 0

    except ClientError as e:
        print(f"S3 download error: {e}")
        return False


def get_vector_index_path() -> str:
    """Get the path to the vector index, downloading from S3 if needed.

    In Lambda: Downloads from S3 to /tmp on first call.
    Locally: Uses the development path if available.

    Returns:
        Path string to the vector index directory.

    Raises:
        FileNotFoundError: If index cannot be found or downloaded.
    """
    # Check if running in Lambda (AWS_EXECUTION_ENV is set)
    is_lambda = "AWS_LAMBDA_FUNCTION_NAME" in os.environ

    if is_lambda:
        # Check if already downloaded to /tmp
        if LOCAL_INDEX_PATH.exists() and any(LOCAL_INDEX_PATH.iterdir()):
            return str(LOCAL_INDEX_PATH)

        # Download from S3
        print(f"Downloading vector index from S3...")
        if download_from_s3(VECTOR_INDEX_BUCKET, VECTOR_INDEX_PREFIX, LOCAL_INDEX_PATH):
            return str(LOCAL_INDEX_PATH)
        else:
            raise FileNotFoundError(
                f"Failed to download vector index from s3://{VECTOR_INDEX_BUCKET}/{VECTOR_INDEX_PREFIX}"
            )
    else:
        # Local development - use env var or default path
        env_path = os.environ.get("VECTOR_INDEX_PATH")
        if env_path and Path(env_path).exists():
            return env_path

        if DEFAULT_DEV_PATH.exists():
            return str(DEFAULT_DEV_PATH)

        raise FileNotFoundError(
            f"Vector index not found. Run 'python scripts/generate_embeddings.py' first."
        )
