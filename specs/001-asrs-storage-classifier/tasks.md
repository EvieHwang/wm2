# Tasks: ASRS Storage Classifier

**Input**: Design documents from `/specs/001-asrs-storage-classifier/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.yaml

**Tests**: Not explicitly requested in specification. Tasks focus on implementation.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- File paths use web app structure: `backend/src/`, `frontend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend directory structure per plan.md: backend/src/agent/, backend/src/agent/tools/, backend/src/models/, backend/src/data/, backend/tests/
- [ ] T002 Create frontend directory structure: frontend/, frontend/assets/
- [ ] T003 Create data directory and add reference CSV: data/wm_weight_and_dim.csv
- [ ] T004 [P] Initialize Python project with requirements.txt in backend/ (anthropic, boto3, pandas)
- [ ] T005 [P] Create SAM template.yaml in backend/ with Lambda, API Gateway, CORS configuration
- [ ] T006 [P] Create .env.example with ANTHROPIC_API_KEY placeholder

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Implement CategoryEnum and CategoryConstraints in backend/src/models/categories.py (5 categories with dimension/weight limits)
- [ ] T008 [P] Implement ClassificationResult and ToolUsageRecord dataclasses in backend/src/models/response.py
- [ ] T009 [P] Implement reference CSV loader in backend/src/data/reference_loader.py (load 479 products into memory)
- [ ] T010 Implement input validation helper for ClassificationRequest in backend/src/handler.py (empty/whitespace check, 2000 char limit)
- [ ] T011 Implement Lambda handler skeleton with /classify POST and /health GET routes in backend/src/handler.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Classify Product from Description (Priority: P1) 🎯 MVP

**Goal**: User enters product description, receives classification (Pouch/Small Bin/Tote/Carton/Oversized) with confidence and reasoning

**Independent Test**: Enter "iPhone 15 Pro Max" → receive classification, confidence 85%+, reasoning mentioning lookup tool

### Implementation for User Story 1

- [ ] T012 [P] [US1] Implement keyword search in backend/src/agent/tools/lookup_product.py (search Product Name, Category, About Product fields)
- [ ] T013 [P] [US1] Implement regex dimension extraction in backend/src/agent/tools/extract_dimensions.py (parse NxNxN, inches, lbs patterns)
- [ ] T014 [US1] Define tool schemas and system prompt in backend/src/agent/prompts.py (tool definitions for Claude API)
- [ ] T015 [US1] Implement classification logic in backend/src/models/categories.py (find smallest category fitting all constraints)
- [ ] T016 [US1] Implement main agent classifier in backend/src/agent/classifier.py (Claude API with tool_choice="auto", process tool calls)
- [ ] T017 [US1] Wire classifier to Lambda handler /classify endpoint in backend/src/handler.py (call classifier, format JSON response)
- [ ] T018 [P] [US1] Create frontend HTML structure in frontend/index.html (text input, submit button, result display area)
- [ ] T019 [P] [US1] Add CSS styling in frontend/styles.css (clean layout, category color coding)
- [ ] T020 [US1] Implement API call and result display in frontend/app.js (fetch /classify, show classification/confidence/reasoning)

**Checkpoint**: User Story 1 functional - can classify products and see results

---

## Phase 4: User Story 2 - View Tool Usage Transparency (Priority: P2)

**Goal**: Results clearly show which tools the agent called (or chose not to call) and why

**Independent Test**: Enter "box 10x8x4 inches" → Tools Used section shows "extract_explicit_dimensions: Called"

### Implementation for User Story 2

- [ ] T021 [US2] Enhance classifier to capture tool invocation details in backend/src/agent/classifier.py (track called/result/reason for each tool)
- [ ] T022 [US2] Update response model to include detailed ToolInvocation in backend/src/models/response.py (ensure JSON includes tools_used structure)
- [ ] T023 [US2] Add Tools Used display section in frontend/index.html (dedicated area for tool status)
- [ ] T024 [US2] Style Tools Used section in frontend/styles.css (visual distinction for called/not called)
- [ ] T025 [US2] Update app.js to render tool usage details in frontend/app.js (show tool name, status, result/reason)

**Checkpoint**: User Stories 1 AND 2 functional - classification with tool transparency

---

## Phase 5: User Story 3 - Understand Classification Categories (Priority: P3)

**Goal**: Users can understand the 5 categories and why their product fits in a specific one

**Independent Test**: View UI → category definitions accessible; reasoning explains why product wouldn't fit smaller categories

### Implementation for User Story 3

- [ ] T026 [US3] Add category reference section to frontend/index.html (collapsible table with L×W×H, weight limits)
- [ ] T027 [US3] Style category reference table in frontend/styles.css (readable formatting, category colors match result badges)
- [ ] T028 [US3] Enhance system prompt in backend/src/agent/prompts.py (instruct Claude to explain why smaller categories don't fit)

**Checkpoint**: All user stories functional - full classification experience with transparency and context

---

## Phase 6: Polish & Deployment

**Purpose**: Production-ready deployment and final improvements

- [ ] T029 [P] Add error handling for Claude API failures in backend/src/agent/classifier.py (timeout, rate limit, invalid response)
- [ ] T030 [P] Add client-side input validation in frontend/app.js (empty input, loading state, error display)
- [ ] T031 [P] Configure CORS properly in backend/template.yaml (allow wm2.evehwang.com origin)
- [ ] T032 Deploy backend with SAM: sam build && sam deploy --guided
- [ ] T033 Deploy frontend to S3: aws s3 sync frontend/ s3://[bucket-name]
- [ ] T034 Configure CloudFront/Route53 for wm2.evehwang.com domain
- [ ] T035 Test end-to-end at wm2.evehwang.com with acceptance scenarios from spec.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
- **Polish & Deployment (Phase 6)**: Depends on at least US1 complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Builds on US1 classifier - can start after T016 complete
- **User Story 3 (P3)**: Can start after Foundational - mostly frontend additions

### Within Each Phase

- Models before services/classifier
- Backend before frontend integration
- Core implementation before polish

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T004 (requirements.txt) || T005 (SAM template) || T006 (.env.example)
```

**Phase 2 (Foundational)**:
```
T008 (response models) || T009 (CSV loader)
```

**User Story 1**:
```
T012 (lookup_product) || T013 (extract_dimensions)  # Backend tools
T018 (HTML) || T019 (CSS)                           # Frontend structure
```

**Polish**:
```
T029 (error handling) || T030 (client validation) || T031 (CORS)
```

---

## Parallel Example: User Story 1 Backend

```bash
# Launch both tools in parallel (different files, no dependencies):
Task: "Implement keyword search in backend/src/agent/tools/lookup_product.py"
Task: "Implement regex dimension extraction in backend/src/agent/tools/extract_dimensions.py"

# Launch frontend structure in parallel:
Task: "Create frontend HTML structure in frontend/index.html"
Task: "Add CSS styling in frontend/styles.css"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T011)
3. Complete Phase 3: User Story 1 (T012-T020)
4. **STOP and VALIDATE**: Test classification end-to-end
5. Deploy to wm2.evehwang.com for demo

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → **MVP: Basic classification works**
3. Add User Story 2 → Tool transparency visible
4. Add User Story 3 → Category education complete
5. Add Polish → Production-ready

### Suggested MVP Scope

**For initial demo/portfolio**: Complete through T020 (User Story 1)
- User can enter description
- System returns classification + confidence + reasoning
- Basic UI displays results
- Tools work but transparency not yet visible in UI

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [US#] label maps task to specific user story
- Reference CSV (wm_weight_and_dim.csv) must be provided by user
- ANTHROPIC_API_KEY required for any Claude API testing
- Local testing with `sam local start-api` before deployment
- All category thresholds are fixed per spec (not user-configurable)
