# MyTraderPal

A trading journal application for tracking trades, strategies, and market observations.

## What it does

Record daily trading notes with direction, session, and risk tracking. Create and manage trading strategies with market specifications. Generate reports on hit/miss performance and session analysis.

## Architecture

API Gateway → Lambda → DynamoDB with Cognito authentication. Infrastructure defined in AWS CDK.

## Requirements

- **Python 3.11+** (backend)
- **Node.js 18+** (frontend/CDK)
- **AWS CLI** (for deployment)
- **AWS CDK v2** (for deployment)

**OS Notes:** Use `source .venv/bin/activate` on macOS/Linux, `.venv\Scripts\activate` on Windows.

## Setup

### Backend
```bash
cd services/api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Frontend
```bash
cd frontend
npm install
```

## Environment Variables

- `TABLE_NAME`: DynamoDB table name (set by CDK for Lambda)
- `DEV_MODE`: Set to `true` to allow `X-MTP-Dev-User` header bypass
- **Optional (for future FastAPI migration):** `USER_POOL_ID`, `USER_POOL_CLIENT_ID`, `AWS_REGION`

## Running

### Frontend Development
```bash
cd frontend
npm run dev
```
Visit `http://localhost:3000`

### Backend Usage (Development)

Use dev identity via header: `X-MTP-Dev-User: <userId>`

**Sample API calls:**

```bash
# Health check
curl -X GET http://localhost:3000/api/v1/health

# Create note
curl -X POST http://localhost:3000/api/v1/notes \
  -H "X-MTP-Dev-User: user123" \
  -H "Content-Type: application/json" \
  -d '{"text": "EUR/USD long", "direction": "LONG", "session": "MORNING"}'

# List notes with pagination
curl -X GET "http://localhost:3000/api/v1/notes?limit=10" \
  -H "X-MTP-Dev-User: user123"

# Create strategy
curl -X POST http://localhost:3000/api/v1/strategies \
  -H "X-MTP-Dev-User: user123" \
  -H "Content-Type: application/json" \
  -d '{"name": "EMA Crossover", "market": "FX", "timeframe": "H1", "dsl": {"entry": "ema20 > ema50"}}'

# Get reports
curl -X GET "http://localhost:3000/api/v1/reports/notes-summary?from=2025-01-01&to=2025-12-31" \
  -H "X-MTP-Dev-User: user123"
```

## Deploy (Optional)

```bash
cd cdk
npm install
cdk synth
cdk bootstrap  # First time only
cdk deploy MyTraderPalStack
```

Find API URL and Cognito IDs in CDK outputs.

## Tests & Coverage

```bash
cd services/api
source .venv/bin/activate
cd ../..
python -m pytest tests/unit/ --cov=services/api --cov-report=term-missing --cov-fail-under=90
```

Tests run offline using mocks/moto - no real AWS required.

## Project Structure

```
mytraderpal/
├── cdk/                    # AWS CDK infrastructure
├── services/api/           # Lambda backend
│   ├── main.py            # Lambda handler
│   └── common/            # Shared modules
├── tests/unit/            # Test suite
└── frontend/              # Next.js frontend
```

## API Summary

- `GET /v1/health` - Health check
- **Notes:** `POST /v1/notes`, `GET /v1/notes`, `PATCH/DELETE /v1/notes/{id}`
- **Strategies:** `POST/GET /v1/strategies`, `GET/PATCH/DELETE /v1/strategies/{id}`
- **Reporting:** `GET /v1/reports/notes-summary?from=&to=&limit=` *(backend-only, not in frontend UI)*

**Auth:** Dev header `X-MTP-Dev-User` vs production JWT (Cognito authorizer)

## Design Notes

- Single-table DynamoDB with GSI1 for queries
- Idempotent writes, pagination, UTC timestamps
- Planned migration to FastAPI/Mangum (unused deps in requirements today)

## Troubleshooting

**Common Issues:**
- **Venv activation:** Use correct path for your OS
- **Missing AWS creds:** Only needed for deployment, not testing
- **CORS errors:** Check Origin header in requests

**Reset environment:** Clear `.env` files and restart services.