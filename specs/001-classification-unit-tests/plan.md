# Implementation Plan: Classification Unit Tests

**Branch**: `001-classification-unit-tests` | **Date**: 2025-12-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from GitHub Issue #46

## Summary

Add comprehensive unit tests for the core classification function and tool helpers that currently have no test coverage. Tests will follow the existing pytest patterns established in `test_feedback.py` (EVE-40), using class-based organization and mocking for external dependencies.

## Technical Context

**Language/Version**: Python 3.11 (Lambda runtime)
**Primary Dependencies**: pytest, unittest.mock, anthropic (mocked)
**Storage**: N/A (unit tests with mocking)
**Testing**: pytest with unittest.mock for API mocking
**Target Platform**: CI/CD pipeline (GitHub Actions via EVE-42)
**Project Type**: Backend Lambda function tests
**Performance Goals**: All tests complete in <30 seconds
**Constraints**: Must mock Claude API calls; no live API calls in unit tests
**Scale/Scope**: ~15-20 test cases covering 3 functions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Test-First | ✅ PASS | This feature IS the tests - implementing test coverage |
| Specification-Driven | ✅ PASS | Tests derived from spec requirements FR-001 through FR-010 |
| Simplicity | ✅ PASS | Following existing test patterns, no new frameworks |

## Project Structure

### Documentation (this feature)

```text
specs/001-classification-unit-tests/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── checklists/
│   └── requirements.md  # Quality checklist
└── contracts/           # N/A for test-only feature
```

### Source Code (repository root)

```text
backend/
├── src/
│   └── agent/
│       ├── classifier.py              # classify_product() - target
│       └── tools/
│           ├── lookup_product.py      # lookup_known_product() - target
│           └── extract_dimensions.py  # extract_explicit_dimensions() - target
└── tests/
    ├── __init__.py
    ├── test_feedback.py               # Existing (EVE-40 pattern)
    └── test_classifier.py             # NEW - this feature
```

**Structure Decision**: Add single new test file `test_classifier.py` to existing `backend/tests/` directory. Follow existing patterns from `test_feedback.py`.

## Complexity Tracking

> No constitution violations - simple test file addition.

---

## Phase 0: Research

### Codebase Analysis

**Functions to Test:**

1. **`classify_product(description: str) -> ClassificationResult`** (classifier.py:107)
   - Returns `ClassificationResult` with: classification (CategoryEnum), confidence (0-100), reasoning (str), tools_used
   - Uses Claude API (must mock `Anthropic` client)
   - Valid categories: POUCH, SMALL_BIN, TOTE, CARTON, OVERSIZED

2. **`lookup_known_product(query: str) -> Dict`** (lookup_product.py:154)
   - Returns dict with: found (bool), matches (list), best_match (dict|None), message (str)
   - Uses reference CSV data and optional semantic search
   - Falls back to keyword search if semantic unavailable

3. **`extract_explicit_dimensions(text: str) -> Dict`** (extract_dimensions.py:140)
   - Returns dict with: found (bool), dimensions (dict), summary (str)
   - Pure function, no external dependencies
   - Parses patterns like "10x8x4 inches", "5 lbs"

**Existing Test Patterns (from test_feedback.py):**
- Class-based organization: `class TestFunctionName:`
- Descriptive method names: `test_specific_scenario`
- Mock decorators: `@patch('src.module.function')`
- Assertions: `assert result == expected`, `assert "text" in result`
- Edge cases: empty strings, None values, boundary conditions

### Dependencies

| Dependency | Purpose | Notes |
|------------|---------|-------|
| pytest | Test runner | Already installed |
| unittest.mock | Mocking | Python stdlib |
| anthropic | API client | Mock only |
| pandas | Reference data | Used by lookup_known_product |

### Decisions

| Decision | Rationale | Alternatives Rejected |
|----------|-----------|----------------------|
| Mock Claude API | Unit tests must be fast and repeatable | Live API calls (slow, costs money, flaky) |
| Single test file | Feature is focused, follows existing pattern | Multiple files (overkill) |
| Class-based tests | Matches existing test_feedback.py style | Function-based (would be inconsistent) |
| Test at function level | Clean isolation, easier debugging | Integration tests only (harder to debug) |

---

## Phase 1: Design

### Test Structure

```python
# backend/tests/test_classifier.py

class TestClassifyProduct:
    """Tests for classify_product function."""
    # FR-001: Valid category returns
    # FR-002: Confidence score range
    # FR-003: Empty/missing description handling

class TestLookupKnownProduct:
    """Tests for lookup_known_product function."""
    # FR-004: Matches products from reference
    # FR-005: Returns empty for unmatched

class TestExtractExplicitDimensions:
    """Tests for extract_explicit_dimensions function."""
    # FR-006: Parses standard dimension formats
    # FR-007: Returns None for no dimensions

class TestEdgeCases:
    """Edge case tests across all functions."""
    # FR-008: Long descriptions, non-English, special chars
```

### Test Cases Mapped to Requirements

| Requirement | Test Case | Assertion |
|-------------|-----------|-----------|
| FR-001 | test_returns_valid_category | `result.classification in CategoryEnum` |
| FR-002 | test_confidence_in_range | `0 <= result.confidence <= 100` |
| FR-003 | test_empty_description | No exception raised |
| FR-003 | test_none_description | Handles gracefully |
| FR-004 | test_lookup_finds_match | `result["found"] == True` |
| FR-005 | test_lookup_no_match | `result["found"] == False` |
| FR-006 | test_parse_standard_dimensions | Correct L×W×H extracted |
| FR-007 | test_no_dimensions_returns_none | `result["found"] == False` |
| FR-008 | test_long_description | No crash, valid result |
| FR-008 | test_unicode_chars | No crash, valid result |
| FR-008 | test_non_english | No crash, valid result |

### Mocking Strategy

```python
# Mock the Anthropic client for classify_product tests
@patch('src.agent.classifier.get_anthropic_client')
def test_classify_product(self, mock_client):
    mock_response = MagicMock()
    mock_response.stop_reason = "end_turn"
    mock_response.content = [MagicMock(text='{"classification": "TOTE", "confidence": 85}')]
    mock_client.return_value.messages.create.return_value = mock_response

    result = classify_product("test product")
    assert result.classification == CategoryEnum.TOTE

# For lookup_known_product - mock reference data
@patch('src.agent.tools.lookup_product.get_reference_data')
def test_lookup_finds_match(self, mock_data):
    mock_data.return_value = pd.DataFrame([...])
```

### Success Criteria Verification

| Criteria | Verification Method |
|----------|---------------------|
| SC-001: 100% tests pass | `pytest backend/tests/test_classifier.py` returns 0 |
| SC-002: Covers 3 areas | Test classes cover classification, tools, edge cases |
| SC-003: 2+ tests per tool | Count tests in TestLookup*, TestExtract* |
| SC-004: 4+ edge cases | Count tests in TestEdgeCases |
| SC-005: <30 seconds | `pytest --durations=0` shows total <30s |
| SC-006: CI compatible | No interactive prompts, no env dependencies |

---

## Quickstart

### Run Tests

```bash
cd backend
pytest tests/test_classifier.py -v
```

### Run All Tests

```bash
cd backend
pytest tests/ -v
```

### Check Coverage

```bash
cd backend
pytest tests/test_classifier.py --cov=src/agent --cov-report=term-missing
```

---

## Next Steps

1. Run `/speckit.tasks` to generate implementation tasks
2. Implement test file following this plan
3. Verify all tests pass
4. Update GitHub Issue #46 with completion status
