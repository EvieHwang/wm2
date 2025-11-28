# Implementation Plan: ASRS Storage Classifier

**Branch**: `001-asrs-storage-classifier` | **Date**: 2025-11-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-asrs-storage-classifier/spec.md`

## Summary

Build an AI-powered product classifier that predicts which ASRS container type (Pouch, Small Bin, Tote, Carton, Oversized) a product should be routed to based on text description. The system uses Claude API with an agentic architecture featuring two optional tools (lookup_known_product, extract_explicit_dimensions) and returns classification, confidence, and reasoning via a web UI at wm2.evehwang.com.

## Technical Context

**Language/Version**: Python 3.11+ (Lambda runtime)
**Primary Dependencies**: Claude API (Anthropic SDK), AWS Lambda, API Gateway, S3
**Storage**: S3 (reference CSV storage)
**Testing**: pytest (unit/integration), manual UI testing
**Target Platform**: AWS Lambda (backend), Static site on S3/CloudFront (frontend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <10 seconds end-to-end response time
**Constraints**: Stateless Lambda functions, cold start considerations, Claude API latency
**Scale/Scope**: Single-user demo/portfolio, no concurrent user requirements for V1

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

> Note: Project constitution is not yet defined (template only). Proceeding with industry best practices.

| Principle | Status | Notes |
|-----------|--------|-------|
| Simplicity | ✅ Pass | Single Lambda, minimal dependencies, no over-engineering |
| Testability | ✅ Pass | Agent logic separable from infrastructure, tool functions unit-testable |
| Observability | ✅ Pass | Structured JSON responses include reasoning and tool usage |
| Security | ✅ Pass | No user data storage, API key secured in environment variables |

## Project Structure

### Documentation (this feature)

```text
specs/001-asrs-storage-classifier/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api.yaml         # OpenAPI specification
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── handler.py           # Lambda entry point
│   ├── agent/
│   │   ├── classifier.py    # Main classification agent logic
│   │   ├── tools/
│   │   │   ├── lookup_product.py      # Reference data lookup tool
│   │   │   └── extract_dimensions.py  # Dimension parsing tool
│   │   └── prompts.py       # System prompts and tool definitions
│   ├── models/
│   │   ├── categories.py    # Category constraints and logic
│   │   └── response.py      # Response data structures
│   └── data/
│       └── reference_loader.py  # CSV loading and search
├── tests/
│   ├── unit/
│   │   ├── test_classifier.py
│   │   ├── test_lookup_product.py
│   │   └── test_extract_dimensions.py
│   └── integration/
│       └── test_handler.py
├── requirements.txt
└── template.yaml            # SAM template for deployment

frontend/
├── index.html               # Single page application
├── styles.css               # Styling
├── app.js                   # UI logic and API calls
└── assets/
    └── (any static assets)

data/
└── wm_weight_and_dim.csv    # Reference product data (479 products)
```

**Structure Decision**: Web application structure with separate backend (Lambda) and frontend (static S3). Backend contains agentic classifier with modular tool functions. Frontend is minimal single-page application.

## Complexity Tracking

No constitution violations to justify. Architecture follows minimal viable approach:
- Single Lambda function (not microservices)
- Direct Claude API calls (no abstraction layers)
- Simple keyword search (not vector/semantic search)
- Static frontend (no framework overhead)
