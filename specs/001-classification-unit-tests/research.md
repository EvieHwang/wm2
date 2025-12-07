# Research: Classification Unit Tests

**Feature**: 001-classification-unit-tests
**Date**: 2025-12-06

## Codebase Analysis

### Functions to Test

| Function | Location | Returns | Dependencies |
|----------|----------|---------|--------------|
| `classify_product` | `src/agent/classifier.py:107` | `ClassificationResult` | Anthropic API, feedback retrieval |
| `lookup_known_product` | `src/agent/tools/lookup_product.py:154` | `Dict` | Reference CSV, optional ChromaDB |
| `extract_explicit_dimensions` | `src/agent/tools/extract_dimensions.py:140` | `Dict` | None (pure function) |

### Valid Classification Categories

From `src/models/categories.py`:
- POUCH
- SMALL_BIN
- TOTE
- CARTON
- OVERSIZED

### Existing Test Patterns

Analyzed `backend/tests/test_feedback.py` (EVE-40):

1. **Organization**: Class-based grouping by function
2. **Naming**: `test_` prefix with descriptive scenario names
3. **Mocking**: `@patch` decorator for external dependencies
4. **Edge cases**: Empty strings, None values, boundary conditions
5. **Assertions**: Direct `assert` statements

### Mocking Requirements

| Function | What to Mock | Why |
|----------|--------------|-----|
| `classify_product` | `get_anthropic_client()` | Avoid live API calls |
| `classify_product` | `get_relevant_feedback()` | Isolate classification logic |
| `lookup_known_product` | `get_reference_data()` | Control test data |
| `lookup_known_product` | `SemanticSearcher` | Avoid ChromaDB dependency |
| `extract_explicit_dimensions` | Nothing | Pure function |

## Design Decisions

### Decision 1: Single Test File

**Choice**: Create one file `test_classifier.py`

**Rationale**:
- Matches existing pattern (one test file per module area)
- Feature is focused on related functions
- Easier to run as a unit

**Alternatives Rejected**:
- Multiple files (overkill for ~15 tests)
- Adding to test_feedback.py (unrelated functionality)

### Decision 2: Mock All External Dependencies

**Choice**: Mock Anthropic client and reference data

**Rationale**:
- Unit tests must be fast (<30s total)
- Repeatable without API keys or data files
- CI environment may not have credentials

**Alternatives Rejected**:
- Live API calls (slow, costs money, flaky)
- Integration tests only (harder to debug failures)

### Decision 3: Class-Based Test Organization

**Choice**: Use `class TestFunctionName:` structure

**Rationale**:
- Matches existing test_feedback.py style
- Clear grouping of related tests
- pytest supports both styles equally

**Alternatives Rejected**:
- Function-based tests (inconsistent with codebase)

## Reference Data

### Sample Test Data

For `lookup_known_product` mocking:
```python
mock_df = pd.DataFrame([
    {
        "Product Name": "Sony WH-1000XM4 Headphones",
        "Category": "Electronics",
        "Product Dimensions": "10 x 8 x 4 inches",
        "Shipping Weight": "0.5 pounds"
    },
    {
        "Product Name": "Large TV Stand",
        "Category": "Furniture",
        "Product Dimensions": "48 x 20 x 30 inches",
        "Shipping Weight": "45 pounds"
    }
])
```

### Dimension Test Cases

| Input | Expected L×W×H | Expected Weight |
|-------|----------------|-----------------|
| "10x8x4 inches" | 10, 8, 4 | None |
| "5 lbs" | None | 5.0 |
| "10x8x4 in, 2.5 lbs" | 10, 8, 4 | 2.5 |
| "no dimensions here" | None | None |
| "" | None | None |

## Dependencies Verified

| Package | Status | Notes |
|---------|--------|-------|
| pytest | ✅ Installed | In pyproject.toml |
| unittest.mock | ✅ Available | Python stdlib |
| pandas | ✅ Installed | Required by lookup_product |
