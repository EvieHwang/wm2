# Feature Specification: ASRS Storage Classifier

**Feature Branch**: `001-asrs-storage-classifier`
**Created**: 2025-11-28
**Status**: Draft
**Input**: User description: "AI-powered product classifier that predicts which ASRS container type a product should be routed to based on text description"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Classify Product from Description (Priority: P1)

A user visits wm2.evehwang.com and enters a product description into a text field. The system analyzes the description using AI, optionally looks up reference data or extracts explicit dimensions, and returns a container classification (Pouch, Small Bin, Tote, Carton, or Oversized) along with a confidence score and reasoning explaining how the decision was made.

**Why this priority**: This is the core value proposition—replacing expensive hardware or manual research with an intelligent API call. Without this, the product has no functionality.

**Independent Test**: Can be fully tested by entering any product description (e.g., "iPhone 15 Pro Max") and verifying the system returns a classification, confidence score, and reasoning that explains the decision process.

**Acceptance Scenarios**:

1. **Given** a user is on wm2.evehwang.com, **When** they enter "iPhone 15 Pro Max" and submit, **Then** they receive a classification (Small Bin), confidence score (85%+), and reasoning mentioning the lookup tool found product data.
2. **Given** a user enters "cotton t-shirt, medium size", **When** they submit, **Then** they receive a classification (Pouch), confidence score (60-80%), and reasoning based on agent inference about apparel dimensions.
3. **Given** a user enters "office desk 60x30 inches", **When** they submit, **Then** they receive a classification (Oversized), confidence score (90%+), and reasoning showing explicit dimensions were extracted.

---

### User Story 2 - View Tool Usage Transparency (Priority: P2)

A user submits a product description and receives results that clearly show which tools the agent called (or chose not to call) and why. This transparency demonstrates intelligent decision-making and builds trust in the classification.

**Why this priority**: Transparency about tool usage is critical for the portfolio/demo use case and distinguishes this from a simple rules-based classifier. It shows the "how" not just the "what."

**Independent Test**: Can be tested by entering descriptions that should trigger different tool combinations and verifying the UI displays accurate tool usage information.

**Acceptance Scenarios**:

1. **Given** a user enters a product with explicit dimensions "box 10x8x4 inches, 5 lbs", **When** they receive results, **Then** the Tools Used section shows "extract_explicit_dimensions: Called - Extracted 10×8×4" and explains why lookup was skipped.
2. **Given** a user enters a known product name "Sony WH-1000XM5 headphones", **When** they receive results, **Then** the Tools Used section shows "lookup_known_product: Called - Found match" with extracted reference data.
3. **Given** a user enters a vague description "small kitchen item", **When** they receive results, **Then** the Tools Used section shows both tools were "Not called" because neither applied.

---

### User Story 3 - Understand Classification Categories (Priority: P3)

A user can understand the five classification categories (Pouch, Small Bin, Tote, Carton, Oversized) and their constraints, so they can interpret results and understand why their product was assigned to a particular category.

**Why this priority**: Category understanding helps users trust and validate the results. However, the primary value is delivered even without explicit category documentation—classification still works.

**Independent Test**: Can be tested by verifying the UI provides clear context about what each classification means and the constraints that define category boundaries.

**Acceptance Scenarios**:

1. **Given** a user receives a classification result, **When** they view the output, **Then** the reasoning explains why the product fits in that category and wouldn't fit in smaller categories.
2. **Given** a user wants to understand the classification system, **When** they look at the UI, **Then** category definitions and constraints are accessible or referenced in the reasoning.

---

### Edge Cases

- What happens when the product description is empty or contains only whitespace?
  - System displays a user-friendly error message prompting for a valid description
- What happens when the description is extremely vague (e.g., "thing")?
  - Agent returns low confidence (40-60%) classification with reasoning explaining the uncertainty
- What happens when explicit dimensions conflict with inferred category (e.g., "tiny item, dimensions 48x36x24")?
  - System prioritizes explicit dimensions over qualitative descriptors
- What happens when the reference lookup returns multiple potential matches?
  - Agent uses the most relevant match based on description similarity and explains the choice
- What happens when network/API errors occur?
  - User receives a clear error message indicating the service is temporarily unavailable
- What happens when dimensions are provided in non-standard formats (e.g., "about 2 feet long")?
  - The extract_explicit_dimensions tool parses approximate measurements and converts units appropriately

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a single text input field for product description on a web page at wm2.evehwang.com
- **FR-002**: System MUST classify products into exactly one of five categories: Pouch, Small Bin, Tote, Carton, or Oversized
- **FR-003**: System MUST return a confidence score (0-100%) with each classification
- **FR-004**: System MUST provide natural language reasoning explaining how the classification was determined
- **FR-005**: System MUST display which tools were used (lookup_known_product, extract_explicit_dimensions) and their outcomes
- **FR-006**: Agent MUST have access to lookup_known_product tool that searches the 479-product reference CSV
- **FR-007**: Agent MUST have access to extract_explicit_dimensions tool that parses weight/dimension values from input text
- **FR-008**: Agent MUST decide whether to call each tool based on input content (tools are optional, not always called)
- **FR-009**: Classification logic MUST assign the smallest category where the product fits within ALL constraints (length, width, height, weight)
- **FR-010**: System MUST return structured JSON responses to support future API access
- **FR-011**: System MUST handle empty or whitespace-only input with a user-friendly error message
- **FR-012**: System MUST prioritize explicit dimensions over qualitative descriptors when both are present
- **FR-013**: Reference data lookup MUST use keyword search against Product Name, Category, and About Product fields

### Category Constraints

| Category   | Max Dimensions (L×W×H)  | Max Weight |
|------------|-------------------------|------------|
| Pouch      | 12" × 9" × 2"           | 1 lb       |
| Small Bin  | 12" × 9" × 6"           | 10 lbs     |
| Tote       | 18" × 14" × 12"         | 50 lbs     |
| Carton     | 24" × 18" × 18"         | 70 lbs     |
| Oversized  | Anything larger         | Any        |

### Confidence Hierarchy

| Source                                         | Confidence Level |
|------------------------------------------------|------------------|
| Explicit dimensions from user (parsed by tool) | High (90%+)      |
| Known product found in reference data          | High (85-95%)    |
| Agent reasoning from description/category      | Medium (60-80%)  |
| Vague or ambiguous description                 | Low (40-60%)     |

### Key Entities

- **Product Description**: User-provided text describing the item to classify; may contain explicit dimensions, product names, or qualitative descriptions
- **Classification Result**: The container category assignment with associated confidence score and reasoning
- **Reference Product**: An entry in the 479-product CSV with known dimensions and weight; used for lookup when description matches
- **Tool Invocation**: Record of which agent tools were called, their inputs, and outputs; displayed for transparency

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can enter a product description and receive classification results within 10 seconds
- **SC-002**: 100% of submissions return one of five valid classifications (Pouch, Small Bin, Tote, Carton, Oversized)
- **SC-003**: 100% of results include a confidence score between 0-100%
- **SC-004**: 100% of results include human-readable reasoning explaining the classification decision
- **SC-005**: 100% of results display tool usage information showing which tools were called and why
- **SC-006**: System is accessible at wm2.evehwang.com with valid SSL certificate
- **SC-007**: Agent demonstrates intelligent tool selection—does not call lookup_known_product for generic descriptions without product identifiers
- **SC-008**: Agent demonstrates intelligent tool selection—does not call extract_explicit_dimensions for descriptions without numeric measurements
- **SC-009**: UI clearly shows HOW the classification was made, suitable for portfolio demonstration and technical evaluation

## Assumptions

- The wm2.evehwang.com domain is already configured and SSL certificate exists in AWS
- The 479-product reference CSV (wm_weight_and_dim.csv) will be provided and contains valid weight/dimension data
- Users have modern web browsers with JavaScript enabled
- Claude API access is available with sufficient quota for the expected usage volume
- V1 keyword search (not semantic search) is acceptable for reference data lookup
- Fixed category thresholds are appropriate for the target use cases

## Scope Boundaries

### In Scope
- Web UI at wm2.evehwang.com
- Single text input for product description
- Classification into 5 fixed categories
- Confidence scoring
- Natural language reasoning
- Tool usage transparency
- Reference data keyword search
- AWS serverless deployment

### Out of Scope (Future Versions)
- API access for programmatic use
- User-configurable category thresholds
- Semantic search in reference data
- Actual weight/dimension output (only classification)
- Accuracy testing dashboard
- Batch processing
- Multiple product classification in single request

## Dependencies

- AWS Lambda, API Gateway, S3 services
- Claude API (Haiku/Sonnet models)
- Reference CSV data file (wm_weight_and_dim.csv)
- wm2.evehwang.com domain with SSL certificate
