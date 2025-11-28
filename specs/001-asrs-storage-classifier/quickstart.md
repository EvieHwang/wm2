# Quickstart: ASRS Storage Classifier

**Feature**: 001-asrs-storage-classifier
**Date**: 2025-11-28

## Prerequisites

- Python 3.11+
- AWS CLI configured with appropriate credentials
- AWS SAM CLI installed
- Anthropic API key

## Environment Setup

```bash
# Clone and navigate to project
cd wm2

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Local Development

### Backend (Lambda Function)

```bash
# Run unit tests
cd backend
pytest tests/unit -v

# Run integration tests (requires API key)
pytest tests/integration -v

# Start local API (SAM)
sam local start-api
```

The API will be available at `http://localhost:3000/classify`

### Frontend

```bash
# Serve frontend locally
cd frontend
python -m http.server 8080
```

Open `http://localhost:8080` in your browser.

## Testing the API

### Using curl

```bash
# Basic classification request
curl -X POST http://localhost:3000/classify \
  -H "Content-Type: application/json" \
  -d '{"description": "Sony WH-1000XM5 headphones"}'

# With explicit dimensions
curl -X POST http://localhost:3000/classify \
  -H "Content-Type: application/json" \
  -d '{"description": "cardboard box 10x8x4 inches, 5 lbs"}'

# Generic description
curl -X POST http://localhost:3000/classify \
  -H "Content-Type: application/json" \
  -d '{"description": "cotton t-shirt medium size"}'
```

### Expected Responses

**Known Product (lookup tool used)**:
```json
{
  "classification": "SMALL_BIN",
  "confidence": 87,
  "reasoning": "Based on product lookup, the Sony WH-1000XM5 has dimensions...",
  "tools_used": {
    "lookup_known_product": {"called": true, "result": "Found match..."},
    "extract_explicit_dimensions": {"called": false, "reason": "No dimensions in input"}
  }
}
```

**Explicit Dimensions (extraction tool used)**:
```json
{
  "classification": "TOTE",
  "confidence": 95,
  "reasoning": "Extracted dimensions 10×8×4 inches and weight 5 lbs...",
  "tools_used": {
    "lookup_known_product": {"called": false, "reason": "Explicit dimensions provided"},
    "extract_explicit_dimensions": {"called": true, "result": "10×8×4 in, 5 lbs"}
  }
}
```

## Deployment

### Deploy to AWS

```bash
# Build the SAM application
sam build

# Deploy (first time - guided)
sam deploy --guided

# Deploy (subsequent)
sam deploy
```

### Frontend Deployment

```bash
# Sync frontend to S3
aws s3 sync frontend/ s3://wm2-frontend-bucket --delete

# Invalidate CloudFront cache (if using)
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

## Project Structure

```
wm2/
├── backend/
│   ├── src/
│   │   ├── handler.py              # Lambda entry point
│   │   ├── agent/
│   │   │   ├── classifier.py       # Main agent logic
│   │   │   ├── tools/
│   │   │   │   ├── lookup_product.py
│   │   │   │   └── extract_dimensions.py
│   │   │   └── prompts.py
│   │   ├── models/
│   │   │   ├── categories.py
│   │   │   └── response.py
│   │   └── data/
│   │       └── reference_loader.py
│   ├── tests/
│   ├── requirements.txt
│   └── template.yaml
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── data/
│   └── wm_weight_and_dim.csv
└── specs/
    └── 001-asrs-storage-classifier/
```

## Key Configuration

### Category Thresholds

| Category | Max L×W×H (in) | Max Weight |
|----------|----------------|------------|
| Pouch | 12×9×2 | 1 lb |
| Small Bin | 12×9×6 | 10 lbs |
| Tote | 18×14×12 | 50 lbs |
| Carton | 24×18×18 | 70 lbs |
| Oversized | ∞ | ∞ |

### Confidence Levels

| Source | Confidence |
|--------|------------|
| Explicit dimensions | 90%+ |
| Reference lookup | 85-95% |
| Agent inference | 60-80% |
| Vague description | 40-60% |

## Troubleshooting

**Lambda cold start slow?**
- First request may take 5-10 seconds
- Subsequent requests should be faster

**API key not working?**
- Verify ANTHROPIC_API_KEY environment variable is set
- Check Lambda environment variables in AWS console

**Classification seems wrong?**
- Check the reasoning in the response
- Verify reference data CSV is loaded correctly
- Test with explicit dimensions to validate logic

## Next Steps

1. Run `/speckit.tasks` to generate implementation tasks
2. Implement backend agent and tools
3. Build frontend UI
4. Deploy and test at wm2.evehwang.com
