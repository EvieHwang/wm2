# WM2 Project Constitution

This document establishes the foundational architectural principles, design philosophy, and decision-making framework for the WM2 project.

## Project Mission

Build an AI-powered supply chain tool that accurately predicts product weights and dimensions from text descriptions, enabling automated logistics planning and cost estimation.

## Architectural Principles

### 1. Serverless-First Architecture

**Rationale**: Minimize operational overhead, maximize scalability, pay only for usage

**Implementation**:
- AWS Lambda for compute workloads
- API Gateway for RESTful API endpoints
- S3 for static assets and data storage
- No servers, containers, or persistent infrastructure to manage

**Trade-offs Accepted**:
- Cold start latency (acceptable for non-real-time predictions)
- AWS vendor lock-in (acceptable for prototype phase)

### 2. AI-Powered Predictions via Claude API

**Rationale**: Leverage state-of-the-art language models for understanding product descriptions

**Implementation**:
- Claude API as the primary inference engine
- Structured output via tool use (not raw text parsing)
- Model selection based on complexity and cost:
  - Claude Haiku: Simple, well-formatted descriptions
  - Claude Sonnet: Complex, ambiguous, or multi-product descriptions
- Fallback strategies for API failures or rate limits

**Trade-offs Accepted**:
- External API dependency (mitigated via retry logic)
- Per-request costs (acceptable given high accuracy requirements)

### 3. Specification-Driven Development

**Rationale**: Reduce ambiguity, improve planning, enable async collaboration

**Implementation**:
- Specifications authored in markdown, stored in `/specs`
- Specs define requirements, API contracts, and acceptance criteria
- Linear issues link to spec files as source of truth
- Implementation follows specs; deviations require spec updates
- Claude Code reads specs before implementing

**Workflow**:
1. Write spec collaboratively (human + AI)
2. Create Linear issues referencing spec files
3. Implement from spec via Claude Code
4. Update spec if reality diverges

### 4. RESTful API Design

**Rationale**: Industry-standard, simple, broadly compatible

**API Principles**:
- JSON request/response bodies
- HTTP status codes for success/error states
- Stateless request handling
- Versioned endpoints (`/v1/predict`)
- Clear error messages with actionable guidance

**Example Endpoint**:
```
POST /v1/predict
Content-Type: application/json

{
  "description": "iPhone 15 Pro Max 256GB in retail box",
  "context": "ecommerce"
}

Response 200 OK:
{
  "weight": {"value": 0.45, "unit": "kg", "confidence": 0.92},
  "dimensions": {"length": 16, "width": 8, "height": 3, "unit": "cm", "confidence": 0.88},
  "modelUsed": "claude-haiku-20250101"
}
```

### 5. Cost-Conscious Model Selection

**Rationale**: Optimize for accuracy per dollar, not raw performance

**Decision Framework**:
- Default to Claude Haiku for standard predictions
- Escalate to Sonnet for:
  - Low confidence scores from Haiku
  - Ambiguous or incomplete descriptions
  - Multi-product or bulk predictions
- Track cost per prediction and accuracy metrics
- Iterate on routing logic based on data

### 6. Prototype Mindset: Deploy Often, Test in Production

**Rationale**: Maximize learning velocity, minimize wasted effort on premature optimization

**Implementation**:
- No staging environment (deploy directly to prod)
- Automated deployment on every commit to main
- Feature flags for experimental changes
- Real-world testing with actual API usage
- Rollback via git revert + redeploy

**Safety Measures**:
- No real users during prototype phase
- API usage capped via AWS budgets and quotas
- Monitoring for cost and error spikes

### 7. Separation of Concerns

**Codebase Organization**:
- `/specs`: Requirements, API contracts, architectural decisions
- `/src`: Application source code (Lambda handlers, utilities)
- `/tests`: Unit and integration tests
- `/docs`: User-facing documentation and guides

**Code Structure**:
- Thin Lambda handlers (routing, validation)
- Reusable business logic in modules
- External API interactions isolated in dedicated modules
- Configuration externalized (environment variables)

## Decision-Making Framework

### When to Update This Constitution

This document should be updated when:
- A new architectural pattern is adopted (e.g., adding a database)
- A core technology choice changes (e.g., switching to a different LLM provider)
- A fundamental design principle is challenged or invalidated

### How Decisions Are Made

1. **Spec-first**: Major changes require a spec document proposing the change
2. **Bias toward action**: When in doubt, prototype and measure
3. **Reversibility**: Prefer decisions that can be easily undone
4. **Data over opinions**: Use metrics to validate assumptions

## Technology Stack

### Core Services
- **Compute**: AWS Lambda (Python runtime)
- **API**: AWS API Gateway (REST API)
- **Storage**: AWS S3
- **Deployment**: AWS SAM or CDK
- **AI**: Anthropic Claude API (Haiku, Sonnet)

### Development Tools
- **Version Control**: Git + GitHub
- **Issue Tracking**: Linear (with MCP integration)
- **Spec Management**: GitHub Spec-Kit
- **AI Coding**: Claude Code

### Languages & Formats
- **Application Code**: Python 3.12+
- **Infrastructure as Code**: SAM templates or CDK (TypeScript)
- **API Contracts**: OpenAPI 3.0 spec
- **Specifications**: Markdown

## Non-Goals (Explicit Out-of-Scope)

To maintain focus, the following are explicitly NOT goals for this project:

1. **Real-time predictions**: Latency under 100ms is not required
2. **Multi-cloud support**: AWS-only is acceptable
3. **On-premise deployment**: Cloud-native only
4. **Complex user authentication**: API key auth is sufficient for prototype
5. **Data persistence beyond S3**: No databases in initial version
6. **Batch processing**: Start with single-item predictions only

## Success Metrics

### Phase 1 (Prototype)
- [ ] API successfully predicts weight and dimensions for 90%+ of test cases
- [ ] Average prediction latency < 5 seconds
- [ ] Cost per prediction < $0.05
- [ ] API uptime > 95%

### Phase 2 (Production-Ready)
- [ ] Prediction accuracy validated against 100+ real products
- [ ] API integrated into at least one supply chain workflow
- [ ] Cost per prediction < $0.02
- [ ] Comprehensive error handling and user feedback

## Revision History

- **2025-11-28**: Initial constitution established
