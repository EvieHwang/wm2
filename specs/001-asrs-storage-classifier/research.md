# Research: ASRS Storage Classifier

**Feature**: 001-asrs-storage-classifier
**Date**: 2025-11-28
**Purpose**: Resolve technical unknowns and document best practices for implementation

## Research Areas

### 1. Claude API Tool Use Pattern

**Decision**: Use Claude's native tool use (function calling) with tool_choice="auto"

**Rationale**:
- Claude natively supports tool definitions and will decide when to call each tool
- Using `tool_choice="auto"` lets the agent skip tools when not needed (matching FR-008)
- Tool results are automatically incorporated into the response
- Anthropic SDK provides clean Python interface

**Alternatives Considered**:
- Manual prompt engineering with JSON parsing: Rejected - less reliable, harder to maintain
- LangChain agents: Rejected - adds dependency overhead for simple 2-tool agent
- Custom orchestration loop: Rejected - Claude's native tool use handles the agentic loop

**Implementation Pattern**:
```python
# Tool definitions passed to API
tools = [
    {
        "name": "lookup_known_product",
        "description": "Search reference database for products matching the description",
        "input_schema": {...}
    },
    {
        "name": "extract_explicit_dimensions",
        "description": "Parse weight/dimension values from input text",
        "input_schema": {...}
    }
]

# Claude decides which tools to call based on input
response = client.messages.create(
    model="claude-3-haiku-20240307",  # or claude-3-sonnet for complex
    tools=tools,
    tool_choice={"type": "auto"},
    messages=[{"role": "user", "content": product_description}]
)
```

### 2. Reference Data Search Strategy

**Decision**: Simple case-insensitive keyword matching against Product Name, Category, and About Product fields

**Rationale**:
- V1 scope explicitly calls for keyword search (not semantic)
- 479 products is small enough to load entirely into memory
- Simple string matching is fast, predictable, and debuggable
- Can return multiple matches ranked by match quality

**Alternatives Considered**:
- Fuzzy matching (fuzzywuzzy): Considered for V1.1 - adds accuracy at cost of complexity
- Vector embeddings (FAISS, Pinecone): Out of scope per spec - V1 uses keyword search
- Full-text search (Elasticsearch): Overkill for 479 products

**Implementation Pattern**:
```python
def search_reference_data(query: str, reference_df: pd.DataFrame) -> list[dict]:
    """Search reference CSV for matching products."""
    query_lower = query.lower()
    keywords = query_lower.split()

    matches = []
    for _, row in reference_df.iterrows():
        searchable = f"{row['Product Name']} {row['Category']} {row['About Product']}".lower()
        score = sum(1 for kw in keywords if kw in searchable)
        if score > 0:
            matches.append((score, row.to_dict()))

    # Return top matches sorted by score
    return [m[1] for m in sorted(matches, key=lambda x: -x[0])[:5]]
```

### 3. Dimension Parsing Approach

**Decision**: Regex-based extraction with unit normalization

**Rationale**:
- Explicit dimensions follow predictable patterns (NxNxN, N inches, N lbs)
- Regex is fast and deterministic
- Can handle common variations (10x8x4, 10"x8"x4", 10 x 8 x 4 inches)
- Unit conversion to inches/pounds for consistency

**Alternatives Considered**:
- LLM-based extraction: Rejected - adds latency, overkill for structured parsing
- NLP entity extraction (spaCy): Rejected - heavy dependency for simple task
- Claude tool output: Could work, but regex is faster and more predictable

**Common Patterns to Match**:
- Dimensions: `10x8x4`, `10"x8"x4"`, `10 x 8 x 4 inches`, `10in x 8in x 4in`
- Weight: `5 lbs`, `5 pounds`, `5lb`, `2.5 kg`, `40 oz`
- Single dimensions: `about 15 inches`, `2 feet long`, `6" tall`

**Implementation Pattern**:
```python
DIMENSION_PATTERNS = [
    r'(\d+(?:\.\d+)?)\s*["\']?\s*[xX×]\s*(\d+(?:\.\d+)?)\s*["\']?\s*[xX×]\s*(\d+(?:\.\d+)?)',
    r'(\d+(?:\.\d+)?)\s*(?:in(?:ch(?:es)?)?|")',
]

WEIGHT_PATTERNS = [
    r'(\d+(?:\.\d+)?)\s*(?:lb(?:s)?|pound(?:s)?)',
    r'(\d+(?:\.\d+)?)\s*(?:kg|kilogram(?:s)?)',
    r'(\d+(?:\.\d+)?)\s*(?:oz|ounce(?:s)?)',
]
```

### 4. Model Selection Strategy

**Decision**: Default to claude-3-haiku, with option to escalate to claude-3-sonnet

**Rationale**:
- Haiku is faster and cheaper - ideal for straightforward classifications
- Sonnet provides better reasoning for ambiguous cases
- User's spec mentions "Haiku for simple cases, Sonnet for complex—agent can decide"
- For V1: Start with Haiku only for simplicity; model escalation can be V1.1

**V1 Implementation**: Use Haiku for all requests
**V1.1 Enhancement**: Add complexity detection to escalate to Sonnet

### 5. AWS Lambda Deployment Pattern

**Decision**: Single Lambda with API Gateway, SAM template for deployment

**Rationale**:
- SAM provides simple infrastructure-as-code for Lambda + API Gateway
- Single Lambda keeps deployment simple
- Environment variables for API keys (not hardcoded)
- S3 for static frontend hosting

**Architecture**:
```
[Static S3 Site] → [API Gateway] → [Lambda] → [Claude API]
                                      ↓
                                 [S3: CSV Data]
```

**SAM Template Key Elements**:
- Lambda function with Python 3.11 runtime
- API Gateway with CORS enabled
- Environment variable for ANTHROPIC_API_KEY
- 30-second timeout (allows for Claude API latency)

### 6. Frontend Architecture

**Decision**: Vanilla HTML/CSS/JS single-page application

**Rationale**:
- Simple demo/portfolio app doesn't need React/Vue overhead
- Faster load times with no framework
- Easy to understand and modify
- Single API call pattern is trivial in vanilla JS

**Key UI Elements**:
- Text input for product description
- Submit button
- Result display area with:
  - Classification badge (color-coded by category)
  - Confidence percentage
  - Reasoning text (collapsible/expandable)
  - Tools Used section

### 7. Error Handling Strategy

**Decision**: Graceful degradation with user-friendly messages

**Rationale**:
- Network errors shouldn't crash the UI
- Claude API errors should show "service temporarily unavailable"
- Empty input validation happens client-side first
- All errors logged server-side for debugging

**Error Categories**:
| Error Type | User Message | Action |
|------------|--------------|--------|
| Empty input | "Please enter a product description" | Block submission |
| Claude API error | "Service temporarily unavailable" | Retry suggestion |
| Timeout | "Request timed out, please try again" | Retry button |
| Invalid response | "Unable to classify product" | Contact support |

### 8. Response Structure

**Decision**: Structured JSON with all required fields

**Rationale**:
- Supports future API access (FR-010)
- Easy to parse in frontend
- Self-documenting structure

**Response Schema**:
```json
{
  "classification": "SMALL_BIN",
  "confidence": 87,
  "reasoning": "Based on the product lookup, the Sony WH-1000XM5 headphones have dimensions of 7.3 x 3.0 x 9.4 inches and weight of 8.8 oz. These fit within the Small Bin constraints (12×9×6 in, 10 lbs) but exceed Pouch depth (2 in max).",
  "tools_used": {
    "lookup_known_product": {
      "called": true,
      "result": "Found match: Sony WH-1000XM5, dimensions 7.3x3.0x9.4 in, weight 8.8 oz"
    },
    "extract_explicit_dimensions": {
      "called": false,
      "reason": "No explicit dimensions in input"
    }
  }
}
```

## Resolved Clarifications

No NEEDS CLARIFICATION items from technical context. User-provided specification was comprehensive.

## Next Steps

1. **Phase 1: Design** - Create data model and API contracts based on research findings
2. **Implementation** - Follow project structure defined in plan.md
3. **Testing** - Unit tests for tools, integration test for full flow
