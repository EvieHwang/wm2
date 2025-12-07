# Tasks: Classification Unit Tests

**Input**: Design documents from `/specs/001-classification-unit-tests/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md

**Tests**: This feature IS the tests - implementing test coverage for classification functions.

**Organization**: Tasks are grouped by user story to enable independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Create test file structure and verify dependencies

- [ ] T001 Create test file backend/tests/test_classifier.py with imports and docstring
- [ ] T002 Add required imports: pytest, unittest.mock, MagicMock, patch
- [ ] T003 [P] Add imports for modules under test: classify_product, lookup_known_product, extract_explicit_dimensions
- [ ] T004 [P] Add import for CategoryEnum from src/models/categories.py
- [ ] T005 Verify pytest runs with empty test file: `cd backend && pytest tests/test_classifier.py -v`

---

## Phase 2: Foundational

**Purpose**: Set up shared test fixtures and mocking utilities

- [ ] T006 Create mock response fixture for Anthropic API in backend/tests/test_classifier.py
- [ ] T007 [P] Create sample product DataFrame fixture for lookup tests in backend/tests/test_classifier.py
- [ ] T008 [P] Create helper function to build mock Claude response in backend/tests/test_classifier.py

**Checkpoint**: Test infrastructure ready - can now implement test classes

---

## Phase 3: User Story 1 - Core Classification Validation (Priority: P1) 🎯 MVP

**Goal**: Test `classify_product()` returns valid categories and confidence scores

**Independent Test**: Run `pytest tests/test_classifier.py::TestClassifyProduct -v` and all tests pass

### Implementation for User Story 1

- [ ] T009 [US1] Create TestClassifyProduct class with docstring in backend/tests/test_classifier.py
- [ ] T010 [US1] Implement test_returns_valid_category: mock API, assert classification in CategoryEnum in backend/tests/test_classifier.py
- [ ] T011 [US1] Implement test_confidence_in_range: mock API, assert 0 <= confidence <= 100 in backend/tests/test_classifier.py
- [ ] T012 [US1] Implement test_empty_description: pass empty string, assert no exception in backend/tests/test_classifier.py
- [ ] T013 [US1] Implement test_none_description: pass None, assert graceful handling in backend/tests/test_classifier.py
- [ ] T014 [US1] Implement test_returns_reasoning: mock API, assert reasoning string present in backend/tests/test_classifier.py
- [ ] T015 [US1] Implement test_tracks_tool_usage: mock API, assert tools_used populated in backend/tests/test_classifier.py
- [ ] T016 [US1] Run TestClassifyProduct tests and verify all pass in backend/tests/test_classifier.py

**Checkpoint**: Core classification tests complete (FR-001, FR-002, FR-003)

---

## Phase 4: User Story 2 - Tool Function Testing (Priority: P2)

**Goal**: Test `lookup_known_product()` and `extract_explicit_dimensions()` work correctly

**Independent Test**: Run `pytest tests/test_classifier.py::TestLookupKnownProduct tests/test_classifier.py::TestExtractExplicitDimensions -v`

### Implementation for User Story 2

- [ ] T017 [US2] Create TestLookupKnownProduct class with docstring in backend/tests/test_classifier.py
- [ ] T018 [US2] Implement test_finds_matching_product: mock reference data, assert found=True in backend/tests/test_classifier.py
- [ ] T019 [US2] Implement test_returns_best_match: mock data with multiple matches, assert best_match populated in backend/tests/test_classifier.py
- [ ] T020 [US2] Implement test_no_match_returns_empty: mock data without match, assert found=False in backend/tests/test_classifier.py
- [ ] T021 [US2] Implement test_empty_query_returns_empty: pass empty string, assert found=False in backend/tests/test_classifier.py
- [ ] T022 [US2] Create TestExtractExplicitDimensions class with docstring in backend/tests/test_classifier.py
- [ ] T023 [US2] Implement test_parses_standard_dimensions: pass "10x8x4 inches", assert correct L/W/H in backend/tests/test_classifier.py
- [ ] T024 [US2] Implement test_parses_weight: pass "5 lbs", assert correct weight in backend/tests/test_classifier.py
- [ ] T025 [US2] Implement test_no_dimensions_returns_not_found: pass text without dimensions, assert found=False in backend/tests/test_classifier.py
- [ ] T026 [US2] Implement test_empty_text_returns_not_found: pass empty string, assert found=False in backend/tests/test_classifier.py
- [ ] T027 [US2] Run tool function tests and verify all pass

**Checkpoint**: Tool function tests complete (FR-004, FR-005, FR-006, FR-007)

---

## Phase 5: User Story 3 - Edge Case Handling (Priority: P3)

**Goal**: Test system handles unusual inputs gracefully

**Independent Test**: Run `pytest tests/test_classifier.py::TestEdgeCases -v`

### Implementation for User Story 3

- [ ] T028 [US3] Create TestEdgeCases class with docstring in backend/tests/test_classifier.py
- [ ] T029 [US3] Implement test_long_description: pass 10000+ char string, assert no crash in backend/tests/test_classifier.py
- [ ] T030 [US3] Implement test_unicode_chars: pass string with emojis/symbols, assert no crash in backend/tests/test_classifier.py
- [ ] T031 [US3] Implement test_non_english_text: pass non-English text, assert no crash in backend/tests/test_classifier.py
- [ ] T032 [US3] Implement test_whitespace_only: pass whitespace string, assert graceful handling in backend/tests/test_classifier.py
- [ ] T033 [US3] Implement test_malformed_dimensions: pass "10x" or "x5x3", assert no crash in backend/tests/test_classifier.py
- [ ] T034 [US3] Implement test_numeric_only_description: pass "12345", assert valid result in backend/tests/test_classifier.py
- [ ] T035 [US3] Run edge case tests and verify all pass

**Checkpoint**: Edge case tests complete (FR-008)

---

## Phase 6: Polish & Verification

**Purpose**: Validate complete test suite and update documentation

- [ ] T036 Run full test suite: `cd backend && pytest tests/test_classifier.py -v`
- [ ] T037 Verify test execution time < 30 seconds: `pytest tests/test_classifier.py --durations=0`
- [ ] T038 Run existing tests to ensure no regression: `cd backend && pytest tests/ -v`
- [ ] T039 Update specs/001-classification-unit-tests/checklists/requirements.md to mark all items complete
- [ ] T040 Commit test file with descriptive message

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can proceed sequentially (recommended) or in parallel
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - Tests core classification
- **User Story 2 (P2)**: Can start after Foundational - Tests tool functions (independent of US1)
- **User Story 3 (P3)**: Can start after Foundational - Tests edge cases (independent of US1/US2)

### Within Each User Story

- Create test class first
- Implement individual test methods
- Run tests to verify before moving on

### Parallel Opportunities

Within Phase 2 (Foundational):
```bash
T007 (mock DataFrame) and T008 (mock helper) can run in parallel
```

All user stories can run in parallel after Foundational:
```bash
Phase 3: TestClassifyProduct (T009-T016)
Phase 4: TestLookupKnownProduct + TestExtractExplicitDimensions (T017-T027)
Phase 5: TestEdgeCases (T028-T035)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T008)
3. Complete Phase 3: User Story 1 (T009-T016)
4. **STOP and VALIDATE**: Core classification tests pass
5. This alone provides value - core function is tested

### Full Implementation

1. Complete Setup + Foundational
2. Complete all 3 user stories
3. Polish and verify (T036-T040)
4. Commit and update GitHub issue

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Tasks** | 40 |
| Setup Tasks | 5 |
| Foundational Tasks | 3 |
| User Story 1 Tasks | 8 |
| User Story 2 Tasks | 11 |
| User Story 3 Tasks | 8 |
| Polish Tasks | 5 |
| **Test Methods** | ~18-20 |

### Requirements Coverage

| Requirement | Test Class | Tasks |
|-------------|------------|-------|
| FR-001, FR-002, FR-003 | TestClassifyProduct | T009-T016 |
| FR-004, FR-005 | TestLookupKnownProduct | T017-T021 |
| FR-006, FR-007 | TestExtractExplicitDimensions | T022-T027 |
| FR-008 | TestEdgeCases | T028-T035 |
| FR-009 | Verified in Polish | T036-T038 |
| FR-010 | Throughout | Following test_feedback.py patterns |

---

## Notes

- All tests in single file: backend/tests/test_classifier.py
- Follow existing patterns from backend/tests/test_feedback.py
- Mock all external dependencies (Anthropic API, reference data)
- Tests must be CI-compatible (no env dependencies, no interactive prompts)
- Target: <30 seconds total execution time
