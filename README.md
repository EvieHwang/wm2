# ASRS Storage Classifier

[![CI](https://github.com/EvieHwang/wm2/actions/workflows/ci.yml/badge.svg)](https://github.com/EvieHwang/wm2/actions/workflows/ci.yml)
[![Deploy](https://github.com/EvieHwang/wm2/actions/workflows/deploy.yml/badge.svg)](https://github.com/EvieHwang/wm2/actions/workflows/deploy.yml)

An AI-powered product classification system that automatically assigns warehouse storage categories based on text descriptions. Built with Claude API and deployed on AWS serverless infrastructure.

**[Live Demo](http://wm2-asrs-classifier-frontend.s3-website-us-west-2.amazonaws.com/)**

## What It Does

Enter a product description, and the classifier determines the optimal ASRS (Automated Storage and Retrieval System) container type. The system uses Claude's reasoning capabilities combined with optional tool calls to:

1. Look up known products in a reference database (479 items)
2. Extract explicit dimensions from the description using regex patterns
3. Apply constraint-based classification rules

## Classification Categories

| Category | Max Dimensions | Max Weight |
|----------|---------------|------------|
| **Pouch** | 10" × 8" × 2" | 1 lb |
| **Small Bin** | 12" × 10" × 6" | 10 lbs |
| **Tote** | 24" × 16" × 12" | 50 lbs |
| **Carton** | 48" × 36" × 36" | 100 lbs |
| **Oversized** | Exceeds carton limits | — |

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────┐
│   Frontend  │────▶│ API Gateway │────▶│  Lambda Function │
│    (S3)     │     │   (CORS)    │     │   (Python 3.12)  │
└─────────────┘     └─────────────┘     └────────┬─────────┘
                                                 │
                                        ┌────────▼─────────┐
                                        │   Claude API     │
                                        │ (Agentic w/Tools)│
                                        └────────┬─────────┘
                                                 │
                              ┌──────────────────┼──────────────────┐
                              ▼                  ▼                  ▼
                    ┌─────────────────┐ ┌───────────────┐ ┌─────────────┐
                    │ lookup_product  │ │ extract_dims  │ │  Classify   │
                    │   (optional)    │ │  (optional)   │ │  (always)   │
                    └─────────────────┘ └───────────────┘ └─────────────┘
```

The agent uses Claude's native tool_choice="auto" to decide whether to call tools based on the input. For recognized products (e.g., "iPhone 14"), it looks up known dimensions. For descriptions with explicit measurements, it extracts them via regex. The final classification applies dimension/weight constraints.

## Feedback Memory

The system learns from user feedback to improve classification accuracy over time:

- **Thumbs up/down**: Users can mark classifications as correct or incorrect
- **Stored in DynamoDB**: Feedback persists globally across all users
- **Few-shot learning**: Relevant feedback is injected into Claude's prompt as examples
- **Two-tier retrieval**: Combines recent feedback + keyword-matched historical entries

## Tech Stack

- **Backend**: Python 3.12, AWS Lambda, API Gateway, SAM, DynamoDB
- **Frontend**: Vanilla HTML/CSS/JavaScript, S3 static hosting
- **AI**: Claude API (Anthropic) with native tool use
- **Data**: CSV reference database with 479 known products

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment:

- **CI**: Runs on all PRs and pushes to main (lint, test, security scan, dependency audit)
- **Deploy**: Automatically deploys to AWS on merge to main

### Required GitHub Secrets

To enable automated deployment, configure these secrets in your GitHub repository:

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key with Lambda, ECR, S3, CodeBuild permissions |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key |
| `ANTHROPIC_API_KEY` | Anthropic API key for running tests |

### Manual Deployment

Prerequisites: AWS CLI configured, SAM CLI installed, Anthropic API key

```bash
# Backend
cd backend
sam build
sam deploy --guided --parameter-overrides AnthropicApiKey=your-key

# Frontend (update API_BASE_URL in app.js first)
aws s3 mb s3://your-bucket-name
aws s3 website s3://your-bucket-name --index-document index.html
aws s3 sync ../frontend s3://your-bucket-name
```

## License

MIT License - See [LICENSE](LICENSE) for details.
