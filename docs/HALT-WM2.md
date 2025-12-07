# HALT-WM2: Agent Evaluation Framework

**Master Context Document**

This document maintains context across the HALT-7 implementation for WM2. It is the single source of truth for decisions made, criteria selected, and progress through the evaluation framework build-out.

---

## Project Overview

**Goal:** Build a systematic agent evaluation system for WM2's ASRS classifier, implementing the HALT framework (Hierarchy, APF, Layers, Traceability) to measure classifier performance and generate actionable improvements.

**Scope:** WM2-specific implementation first. Learnings will inform a generalizable framework later.

**Key Principle:** Build incrementally, refine through conversation before speccing each phase.

---

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Dashboard location | New page at wm2.evehwang.com | Separate from main classifier UI |
| Results storage | TBD (DynamoDB vs SQLite) | To be decided in Phase 3 |
| Test data source | Holdout set from 479-row CSV | Excluded from ChromaDB embeddings |
| Eval trigger | Manual | PM-initiated batch evaluation runs |
| Existing feedback | Separate loop | User thumbs up/down ≠ PM eval workflow |

---

## Phase Structure

### Phase 1: Define What Good Means
- [ ] HALT-1: WM2 Criteria Mapping
- [ ] HALT-2: WM2 Signal Inventory
- [ ] HALT-3: Signal-to-Criteria Binding

### Phase 2: Create Test Infrastructure
- [ ] HALT-4: Test Data Holdout Set
- [ ] HALT-5: Test Specifications
- [ ] HALT-6: Test Catalog

### Phase 3: Execute and Display
- [ ] HALT-7: Test Execution Engine
- [ ] HALT-8: Dashboard Tiers 1-2

### Phase 4: Human-in-the-Loop
- [ ] HALT-9: Dashboard Tier 3
- [ ] HALT-10: Evaluation &amp; Prioritization

### Phase 5: Close the Loop
- [ ] HALT-11: Issue Generation Engine

---

## WM2 Criteria Selection

*To be populated after HALT-1 conversation*

### Effectiveness Pillar
| Criterion | Relevance | Notes |
|-----------|-----------|-------|
| Accuracy/Correctness | | |
| Completeness | | |
| Consistency/Stability | | |

### Efficiency Pillar
| Criterion | Relevance | Notes |
|-----------|-----------|-------|
| Tool Accuracy | | |
| Tool Efficiency | | |
| Latency | | |
| Cost Efficiency | | |

### Reliability Pillar
| Criterion | Relevance | Notes |
|-----------|-----------|-------|
| Variance Across Runs | | |
| Context Recall | | |

### Trustworthiness Pillar
| Criterion | Relevance | Notes |
|-----------|-----------|-------|
| Transparency | | |
| Groundedness/Citations | | |
| Safety/Risk | | |

---

## Signal Inventory

*To be populated after HALT-2 conversation*

### Currently Observable
| Signal | Source | Data Type |
|--------|--------|-----------|
| | | |

### Gaps Identified
| Missing Signal | Required For | Instrumentation Needed |
|----------------|--------------|------------------------|
| | | |

---

## Binding Table

*To be populated after HALT-3 conversation*

| Criterion | Signal(s) | Derivation | Metric Type |
|-----------|-----------|------------|-------------|
| | | | |

---

## Test Data

*To be populated after HALT-4 conversation*

- **Holdout size:** TBD
- **Stratification:** By category (Pouch, Small Bin, Tote, Carton, Oversized)
- **ChromaDB exclusion method:** TBD

---

## Progress Log

| Date | Issue | Status | Key Decisions |
|------|-------|--------|---------------|
| 2025-12-06 | Setup | Created | Master doc, GitHub issues created |

---

## Links

- [GitHub Issue #50: Original HALT-7 Spec](https://github.com/EvieHwang/wm2/issues/50)
- [HALT Framework Reference](/docs/HALT-framework.md)
- [WM2 Live App](https://wm2.evehwang.com)
