#!/usr/bin/env python3
"""Evaluate semantic search quality against test cases from spec."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.tools.lookup_product import lookup_known_product


# Test cases from EVE-47 spec
SEMANTIC_TEST_CASES = [
    # Semantic queries - should find related products
    {"query": "electric scooter", "expected_contains": ["scooter"], "type": "semantic"},
    {"query": "hoverboard", "expected_contains": ["hover", "swag"], "type": "semantic"},
    {"query": "kids toy", "expected_contains": ["kid", "toy", "child"], "type": "semantic"},
    {"query": "pet accessories", "expected_contains": ["dog", "pet", "costume"], "type": "semantic"},
]

KEYWORD_PARITY_CASES = [
    # Keyword queries - exact matches should work
    {"query": "Segway Ninebot", "expected_top": "Segway Ninebot ES1", "type": "keyword"},
    {"query": "Swagtron", "expected_top": "Swagtron", "type": "keyword"},
    {"query": "Razor scooter", "expected_top": "Razor", "type": "keyword"},
    {"query": "Ghostbusters dog", "expected_top": "Ghostbusters", "type": "keyword"},
]


def check_contains(product_name: str, expected_keywords: list) -> bool:
    """Check if product name contains any expected keyword."""
    name_lower = product_name.lower()
    return any(kw.lower() in name_lower for kw in expected_keywords)


def run_tests():
    print("=" * 60)
    print("SEMANTIC SEARCH EVALUATION")
    print("=" * 60)

    # Semantic test cases
    print("\n### Semantic Query Tests ###")
    semantic_passed = 0
    for case in SEMANTIC_TEST_CASES:
        start = time.time()
        result = lookup_known_product(case["query"])
        latency = (time.time() - start) * 1000

        if result["found"]:
            top_name = result["best_match"]["product_name"]
            similarity = result["best_match"].get("similarity", 0)
            passed = check_contains(top_name, case["expected_contains"])

            status = "PASS" if passed else "FAIL"
            if passed:
                semantic_passed += 1

            print(f"\n{status}: '{case['query']}'")
            print(f"  Top result: {top_name[:60]}...")
            print(f"  Similarity: {similarity:.2f}, Latency: {latency:.0f}ms")
        else:
            print(f"\nFAIL: '{case['query']}' - No results found")

    # Keyword parity test cases
    print("\n\n### Keyword Parity Tests ###")
    keyword_passed = 0
    for case in KEYWORD_PARITY_CASES:
        start = time.time()
        result = lookup_known_product(case["query"])
        latency = (time.time() - start) * 1000

        if result["found"]:
            top_name = result["best_match"]["product_name"]
            similarity = result["best_match"].get("similarity", 0)
            passed = case["expected_top"].lower() in top_name.lower()

            status = "PASS" if passed else "FAIL"
            if passed:
                keyword_passed += 1

            print(f"\n{status}: '{case['query']}'")
            print(f"  Expected: {case['expected_top']}")
            print(f"  Got: {top_name[:60]}...")
            print(f"  Similarity: {similarity:.2f}, Latency: {latency:.0f}ms")
        else:
            print(f"\nFAIL: '{case['query']}' - No results found")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Semantic tests: {semantic_passed}/{len(SEMANTIC_TEST_CASES)} passed")
    print(f"Keyword tests:  {keyword_passed}/{len(KEYWORD_PARITY_CASES)} passed")
    print(f"Total:          {semantic_passed + keyword_passed}/{len(SEMANTIC_TEST_CASES) + len(KEYWORD_PARITY_CASES)} passed")

    return semantic_passed + keyword_passed == len(SEMANTIC_TEST_CASES) + len(KEYWORD_PARITY_CASES)


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
