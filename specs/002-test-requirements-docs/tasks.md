# Tasks: Test Requirements Documentation

**Input**: Design documents from `/specs/002-test-requirements-docs/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md

**Tests**: Not required - this is a documentation-only feature.

**Organization**: Tasks are grouped by user story to enable independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Verify current state of files to be modified

- [ ] T001 Verify CONSTITUTION.md exists and has Specification-Driven Development section at specs/CONSTITUTION.md
- [ ] T002 [P] Verify spec-template.md exists at .specify/templates/spec-template.md
- [ ] T003 [P] Verify checklist-template.md exists at .specify/templates/checklist-template.md

---

## Phase 2: Foundational

**Purpose**: No blocking prerequisites for documentation updates

> This phase is empty - documentation updates have no foundational dependencies.

**Checkpoint**: Ready to proceed with user story implementation

---

## Phase 3: User Story 1 - Constitution Testing Policy (Priority: P1) 🎯 MVP

**Goal**: Add Testing Requirements section to CONSTITUTION.md so contributors understand tests are mandatory

**Independent Test**: Read CONSTITUTION.md and verify Testing Requirements subsection exists with mandatory test guidance

### Implementation for User Story 1

- [ ] T004 [US1] Add Testing Requirements subsection after line 56 in specs/CONSTITUTION.md
- [ ] T005 [US1] Include mandatory test types (unit tests, happy path, edge cases) in specs/CONSTITUTION.md
- [ ] T006 [US1] Add "tests must pass before merge" requirement in specs/CONSTITUTION.md
- [ ] T007 [US1] Include test location (/backend/tests/) and runner (pytest) in specs/CONSTITUTION.md
- [ ] T008 [US1] Add reference to test_feedback.py as pattern example in specs/CONSTITUTION.md
- [ ] T009 [US1] Add exceptions clause for pure documentation changes in specs/CONSTITUTION.md

**Checkpoint**: CONSTITUTION.md now contains complete Testing Requirements section (FR-001 through FR-005, FR-009)

---

## Phase 4: User Story 2 - Spec Template Test Section (Priority: P2)

**Goal**: Add Test Requirements section to spec template so feature authors plan for tests

**Independent Test**: Check spec-template.md includes Test Requirements section with prompts for test coverage

### Implementation for User Story 2

- [ ] T010 [US2] Add "## Test Requirements *(mandatory)*" section before Success Criteria in .specify/templates/spec-template.md
- [ ] T011 [US2] Add "What to Test" checklist prompts in .specify/templates/spec-template.md
- [ ] T012 [US2] Add "Test Coverage" section with unit/integration prompts in .specify/templates/spec-template.md
- [ ] T013 [US2] Add "Test Location" placeholder in .specify/templates/spec-template.md
- [ ] T014 [US2] Add instruction comment referencing CONSTITUTION.md in .specify/templates/spec-template.md

**Checkpoint**: spec-template.md now contains Test Requirements section (FR-006, FR-007)

---

## Phase 5: User Story 3 - Acceptance Criteria Checkbox (Priority: P3)

**Goal**: Add test checkbox to checklist template so reviewers verify tests are complete

**Independent Test**: Check checklist-template.md includes "Tests written and passing" checkbox

### Implementation for User Story 3

- [ ] T015 [US3] Add "## Implementation" section to .specify/templates/checklist-template.md
- [ ] T016 [US3] Add "Tests written and passing" checkbox in .specify/templates/checklist-template.md
- [ ] T017 [US3] Add "Test coverage meets requirements from spec" checkbox in .specify/templates/checklist-template.md

**Checkpoint**: checklist-template.md now contains test checkboxes (FR-008)

---

## Phase 6: Polish & Verification

**Purpose**: Validate all changes work together

- [ ] T018 Review all 3 files for internal consistency (no conflicting guidance)
- [ ] T019 Verify new spec creation includes Test Requirements section (test with create-new-feature.sh)
- [ ] T020 Update specs/002-test-requirements-docs/checklists/requirements.md to mark all items complete
- [ ] T021 Commit all changes with descriptive message

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - verification only
- **Foundational (Phase 2)**: Empty for this feature
- **User Stories (Phase 3-5)**: All independent - can proceed in parallel
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies - modifies CONSTITUTION.md only
- **User Story 2 (P2)**: No dependencies - modifies spec-template.md only
- **User Story 3 (P3)**: No dependencies - modifies checklist-template.md only

### Parallel Opportunities

All user stories modify different files and can be executed in parallel:

```bash
# All user story phases can run in parallel:
Phase 3: CONSTITUTION.md updates (T004-T009)
Phase 4: spec-template.md updates (T010-T014)
Phase 5: checklist-template.md updates (T015-T017)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (verify files exist)
2. Complete Phase 3: User Story 1 (CONSTITUTION.md)
3. **STOP and VALIDATE**: Constitution now has testing requirements
4. This alone provides value - contributors know tests are required

### Full Implementation

1. Complete Setup (T001-T003)
2. Execute all user stories in parallel (T004-T017)
3. Polish and verify (T018-T021)
4. Commit and update GitHub issue

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 21 |
| User Story 1 Tasks | 6 |
| User Story 2 Tasks | 5 |
| User Story 3 Tasks | 3 |
| Setup Tasks | 3 |
| Polish Tasks | 4 |
| Parallel Opportunities | All user stories (3 phases) |

---

## Notes

- All tasks modify markdown files only
- No tests required (documentation feature)
- Each user story modifies a single file
- All user stories are fully independent
- Commit after completing each user story for incremental progress
