# Data Model: ASRS Storage Classifier

**Feature**: 001-asrs-storage-classifier
**Date**: 2025-11-28

## Entities

### ClassificationRequest

The input from a user requesting product classification.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| description | string | Yes | Product description text (1-2000 characters) |

**Validation Rules**:
- Description must not be empty or whitespace-only
- Description must not exceed 2000 characters
- No special character restrictions (product names may include symbols)

---

### ClassificationResult

The output of a classification request.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| classification | CategoryEnum | Yes | Assigned container category |
| confidence | integer | Yes | Confidence percentage (0-100) |
| reasoning | string | Yes | Natural language explanation of decision |
| tools_used | ToolUsageRecord | Yes | Details of which tools were called |

---

### CategoryEnum

Enumeration of valid container categories.

| Value | Display Name | Description |
|-------|--------------|-------------|
| POUCH | Pouch | Smallest category for apparel, soft goods |
| SMALL_BIN | Small Bin | Electronics, small parts, cosmetics |
| TOTE | Tote | General merchandise, packaged goods |
| CARTON | Carton | Bulky items, multi-packs |
| OVERSIZED | Oversized | Anything exceeding Carton limits |

---

### CategoryConstraints

Defines the dimensional and weight limits for each category.

| Field | Type | Description |
|-------|------|-------------|
| category | CategoryEnum | The category these constraints apply to |
| max_length | float | Maximum length in inches |
| max_width | float | Maximum width in inches |
| max_height | float | Maximum height in inches |
| max_weight | float | Maximum weight in pounds |

**Constraint Values**:

| Category | Max L (in) | Max W (in) | Max H (in) | Max Weight (lbs) |
|----------|------------|------------|------------|------------------|
| POUCH | 12 | 9 | 2 | 1 |
| SMALL_BIN | 12 | 9 | 6 | 10 |
| TOTE | 18 | 14 | 12 | 50 |
| CARTON | 24 | 18 | 18 | 70 |
| OVERSIZED | ∞ | ∞ | ∞ | ∞ |

---

### ToolUsageRecord

Records which agent tools were called during classification.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| lookup_known_product | ToolInvocation | Yes | Status of product lookup tool |
| extract_explicit_dimensions | ToolInvocation | Yes | Status of dimension extraction tool |

---

### ToolInvocation

Details about a single tool's usage.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| called | boolean | Yes | Whether the tool was invoked |
| result | string | No | Tool output if called (null if not called) |
| reason | string | No | Why tool was/wasn't called |

---

### ReferenceProduct

A product from the reference dataset with known dimensions.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| product_name | string | Yes | Name of the product |
| category | string | Yes | Product category (e.g., Electronics, Apparel) |
| model_number | string | No | Manufacturer model number |
| about_product | string | No | Product description text |
| technical_details | string | No | Technical specifications |
| shipping_weight | string | Yes | Weight as string (e.g., "1.5 pounds") |
| product_dimensions | string | Yes | Dimensions as string (e.g., "10 x 8 x 4 inches") |

**Source**: wm_weight_and_dim.csv (479 products)

---

### ParsedDimensions

Structured dimensions extracted from text or reference data.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| length | float | No | Length in inches (null if unknown) |
| width | float | No | Width in inches (null if unknown) |
| height | float | No | Height in inches (null if unknown) |
| weight | float | No | Weight in pounds (null if unknown) |
| source | string | Yes | Where data came from: "explicit", "reference", "inferred" |

---

## Relationships

```
ClassificationRequest (1) ──creates──> (1) ClassificationResult
                                              │
                                              ├── contains (1) CategoryEnum
                                              └── contains (1) ToolUsageRecord
                                                                  │
                                                                  └── contains (2) ToolInvocation

ReferenceProduct (479) ──searched by──> lookup_known_product tool
                                              │
                                              └── produces ParsedDimensions

User Input Text ──parsed by──> extract_explicit_dimensions tool
                                              │
                                              └── produces ParsedDimensions

ParsedDimensions ──compared against──> CategoryConstraints
                                              │
                                              └── determines CategoryEnum
```

## State Transitions

### Classification Request Lifecycle

```
[Input Received]
       │
       ▼
[Validate Input] ──invalid──> [Return Error]
       │
       │ valid
       ▼
[Agent Processing]
       │
       ├── (optional) Call lookup_known_product
       │         │
       │         └── Returns: match/no match + dimensions
       │
       ├── (optional) Call extract_explicit_dimensions
       │         │
       │         └── Returns: parsed dimensions
       │
       ▼
[Determine Classification]
       │
       ├── Has explicit dimensions? ──> High confidence (90%+)
       ├── Found reference match? ──> High confidence (85-95%)
       ├── Inferred from description? ──> Medium confidence (60-80%)
       └── Vague input? ──> Low confidence (40-60%)
       │
       ▼
[Return ClassificationResult]
```

## Data Storage

### Runtime Data (No Persistence)
- ClassificationRequest: Exists only during request processing
- ClassificationResult: Returned to client, not stored
- ToolInvocation: Part of response, not stored

### Static Data (Read-Only)
- ReferenceProduct: Loaded from CSV on Lambda cold start
- CategoryConstraints: Hardcoded constants

### Configuration (Environment Variables)
- ANTHROPIC_API_KEY: Claude API authentication
- REFERENCE_DATA_PATH: S3 path to CSV file (or bundled with Lambda)
