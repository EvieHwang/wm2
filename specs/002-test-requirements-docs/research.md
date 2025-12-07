# Research: Test Requirements Documentation

**Feature**: 002-test-requirements-docs
**Date**: 2025-12-06

## Files to Update

| File | Purpose | Current State |
|------|---------|---------------|
| `specs/CONSTITUTION.md` | Project governance | Has Spec-Driven section, no test requirements |
| `.specify/templates/spec-template.md` | Feature spec template | No Test Requirements section |
| `.specify/templates/checklist-template.md` | Completion checklist | No test checkbox |

## Current Documentation Analysis

### CONSTITUTION.md

Location: `/Users/evehwang/GitHub/wm2/specs/CONSTITUTION.md`

Current sections:
1. Project Mission
2. Architectural Principles (1-7)
3. Decision-Making Framework
4. Technology Stack
5. Non-Goals
6. Success Metrics
7. Revision History

Section 3 ("Specification-Driven Development") covers specs workflow but has no testing requirements.
Section 6 mentions "Test in Production" but doesn't require automated tests.

### Spec Template

Location: `/Users/evehwang/GitHub/wm2/.specify/templates/spec-template.md`

Current sections:
- Feature header
- User Scenarios & Testing
- Requirements (Functional, Key Entities)
- Success Criteria

Missing: Test Requirements section to define what tests are needed.

### Checklist Template

Location: `/Users/evehwang/GitHub/wm2/.specify/templates/checklist-template.md`

Current structure:
- Generic template with placeholders
- Categories for different checklist types
- No default test-related items

## Reference: Existing Test Patterns

**EVE-40 Feedback Tests** (`backend/tests/test_feedback.py`):
- 248 lines, ~26 test methods
- 6 test classes organized by function
- Uses pytest with unittest.mock
- Covers: tokenization, keywords, retrieval, formatting, validation

**Pattern Highlights**:
```python
class TestFunctionName:
    """Tests for function_name function."""

    def test_happy_path(self):
        result = function_name("valid input")
        assert result == expected

    def test_empty_input(self):
        result = function_name("")
        assert result == []

    @patch('module.dependency')
    def test_with_mock(self, mock_dep):
        mock_dep.return_value = mock_value
        result = function_name("input")
        assert result.used_mock
```

## Design Decisions

### Decision 1: Add to Section 3

**Choice**: Add Testing Requirements as subsection under "Specification-Driven Development"

**Rationale**: Testing is integral to the spec workflow - specs should define tests, tests validate specs.

**Alternatives Rejected**:
- New top-level section: Would fragment related content
- Under "Prototype Mindset": Tests are more about quality than velocity

### Decision 2: Simple Language

**Choice**: Describe requirements in plain language (happy path, edge cases)

**Rationale**: Must be understood by all contributors, not just developers

**Alternatives Rejected**:
- Coverage percentages: Hard to enforce, varies by feature
- Complex test taxonomies: Overkill for prototype phase

### Decision 3: Reference Examples

**Choice**: Point to `test_feedback.py` as the pattern to follow

**Rationale**: Concrete examples are more actionable than abstract guidelines

**Alternatives Rejected**:
- Write new example tests: Duplicates existing good examples
- Link to external resources: Less relevant to this codebase

### Decision 4: Allow Exceptions

**Choice**: Allow skipping tests for pure documentation/config changes

**Rationale**: Some changes genuinely don't need tests (README updates, etc.)

**Alternatives Rejected**:
- No exceptions: Would create unnecessary friction
- Complex exception rules: Hard to remember and apply

## Content to Add

### CONSTITUTION.md Addition

Insert after line 56 (after "Update spec if reality diverges"):

```markdown
### Testing Requirements

All features must ship with automated tests:

- **Unit tests** for new functions and modules
- **Happy path** coverage for primary use cases
- **Edge case** coverage for error conditions and boundaries
- Tests must **pass before merge** to main

**Test Location**: `/backend/tests/`
**Test Runner**: `pytest`
**Reference**: See `test_feedback.py` for patterns (EVE-40)

**Exceptions**: Pure documentation or configuration changes may skip tests with justification in the PR description.
```

### Spec Template Addition

Insert before "## Success Criteria":

```markdown
## Test Requirements *(mandatory)*

### What to Test
- [ ] [Core functionality tests]
- [ ] [Edge case tests]
- [ ] [Integration tests if applicable]

### Test Coverage
- **Unit tests**: [List functions/modules]
- **Integration tests**: [List or N/A]

### Test Location
Tests will be added to: `[path]`
```

### Checklist Template Addition

Add default category:

```markdown
## Implementation

- [ ] Tests written and passing
- [ ] Test coverage meets requirements from spec
```

## Verification Plan

1. Read each file after update to verify content
2. Create test spec to verify template works
3. Manual review for consistency across all 3 files
