#!/usr/bin/env python3
"""Generate embeddings for all products and persist to ChromaDB.

One-time offline script to create vector index for semantic search.
Run from backend directory: python scripts/generate_embeddings.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer


# Configuration
MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "product_embeddings"
CSV_PATH = Path(__file__).parent.parent.parent / "data" / "wm_weight_and_dim.csv"
INDEX_PATH = Path(__file__).parent.parent / "data" / "vector_index"


def build_embedding_text(row: dict) -> str:
    """Build text to embed from product fields.

    Combines product name, category, and description for semantic matching.
    """
    name = str(row.get("Product Name", "") or "")
    category = str(row.get("Category", "") or "")
    about = str(row.get("About Product", "") or "")

    parts = [name]
    if category:
        parts.append(f"Category: {category}")
    if about:
        parts.append(about)

    return ". ".join(parts)


def main():
    print(f"Loading CSV from {CSV_PATH}")
    if not CSV_PATH.exists():
        print(f"ERROR: CSV not found at {CSV_PATH}")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} products")

    # Initialize embedding model
    print(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    # Prepare documents and metadata
    documents = []
    metadatas = []
    ids = []

    for idx, row in df.iterrows():
        doc_text = build_embedding_text(row)
        documents.append(doc_text)

        # Store all original fields as metadata
        metadata = {}
        for col in df.columns:
            val = row[col]
            # ChromaDB requires string, int, float, or bool metadata values
            if pd.isna(val):
                metadata[col] = ""
            else:
                metadata[col] = str(val)
        metadatas.append(metadata)

        # Use Uniq Id if available, otherwise row index
        doc_id = str(row.get("Uniq Id", idx))
        ids.append(doc_id)

    # Generate embeddings in batch
    print("Generating embeddings...")
    embeddings = model.encode(documents, show_progress_bar=True)
    print(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])}")

    # Create/recreate ChromaDB collection
    print(f"Creating ChromaDB collection at {INDEX_PATH}")
    INDEX_PATH.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(INDEX_PATH))

    # Delete existing collection if it exists (idempotent)
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection: {COLLECTION_NAME}")

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}  # Use cosine similarity
    )

    # Add documents with embeddings
    print("Adding documents to collection...")
    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=documents,
        metadatas=metadatas
    )

    print(f"Successfully indexed {collection.count()} products")

    # Verify by running a test query
    print("\nTest query: 'electric scooter'")
    test_results = collection.query(
        query_embeddings=[model.encode("electric scooter").tolist()],
        n_results=3
    )

    print("Top 3 results:")
    for i, (doc_id, metadata) in enumerate(zip(test_results["ids"][0], test_results["metadatas"][0])):
        print(f"  {i+1}. {metadata.get('Product Name', 'Unknown')}")

    print(f"\nDone! Index persisted to {INDEX_PATH}")


if __name__ == "__main__":
    main()
