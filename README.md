# MyTraderPal

A trading journal application for tracking trades, strategies, and market observations.

## What it does

Record daily trading notes with direction, session, and risk tracking. Create and manage trading strategies with market specifications. Generate reports on hit/miss performance and session analysis.

## Architecture

API Gateway → Lambda → DynamoDB with Cognito authentication. Infrastructure defined in AWS CDK.

**Modern Architecture:**
- Layered architecture (API → Services → Repositories)
- SOLID principles applied
- Comprehensive monitoring and metrics
- CI/CD pipeline with automated testing
- Docker containerization
- Health checks and Prometheus metrics

## Requirements

- **Python 3.11+** (backend)
- **Node.js 18+** (frontend/CDK)
- **AWS CLI** (for deployment)
- **AWS CDK v2** (for deployment)
- **Docker** (for containerization, optional)

**OS Notes:** Use `source .venv/bin/activate` on macOS/Linux, `.venv\Scripts\activate` on Windows.

## Project Structure

```
mytraderpal/
├── src/
│   ├── app/                 # Backend application
│   │   ├── main.py         # Lambda handler entry point
│   │   ├── api/            # Controllers (route handlers)
│   │   │   ├── router.py   # Request routing
│   │   │   ├── notes.py    # Notes endpoints
│   │   │   ├── strategies.py # Strategies endpoints
│   │   │   ├── reports.py  # Reports endpoints
│   │   │   └── metrics.py  # Metrics endpoint
│   │   ├── core/           # Core utilities
│   │   │   ├── auth.py     # Authentication
│   │   │   ├── response.py # HTTP response helpers
│   │   │   ├── utils.py    # General utilities
│   │   │   ├── metrics.py  # Metrics collection
│   │   │   └── health.py   # Health check logic
│   │   ├── models/         # Domain models
│   │   │   ├── note.py
│   │   │   └── strategy.py
│   │   ├── services/        # Business logic
│   │   │   ├── note_service.py
│   │   │   ├── strategy_service.py
│   │   │   └── report_service.py
│   │   └── repositories/   # Data access
│   │       └── dynamodb.py
│   └── frontend/           # Next.js frontend
│       ├── app/
│       ├── components/
│       └── lib/
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── infra/
│   ├── cdk/                # AWS CDK infrastructure
│   └── docker/             # Docker files
├── docs/                   # Documentation
│   ├── SDLC.md            # SDLC model explanation
│   ├── ARCHITECTURE.md     # Architecture diagrams
│   └── REPORT.md          # Assignment 2 report
├── scripts/                # Utility scripts
│   ├── test.sh
│   ├── lint.sh
│   ├── deploy.sh
│   └── run_local.sh
├── monitoring/             # Monitoring configs
│   ├── prometheus.yml
│   └── grafana-dashboard.json
├── .github/workflows/      # CI/CD pipelines
│   └── ci.yml
├── Dockerfile              # Backend container
├── docker-compose.yml      # Local development
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Dev dependencies
└── README.md
```

## Setup

### Backend

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Frontend

```bash
cd src/frontend
npm install
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

See `.env.example` for all required variables.

## Running

### Local Development

**Backend:**
```bash
# Using scripts
./scripts/run_local.sh

# Or manually with Docker
docker-compose up
```

**Frontend:**
```bash
cd src/frontend
npm run dev
```

Visit `http://localhost:3000`

### Using Scripts

```bash
# Run tests
./scripts/test.sh

# Run linter
./scripts/lint.sh

# Deploy to AWS
./scripts/deploy.sh

# Run locally
./scripts/run_local.sh
```

## Tests & Coverage

### Run Tests

```bash
python -m pytest tests/unit/ \
  --cov=src/app \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-fail-under=70 \
  -v
```

**Coverage**: 84% (exceeds 70% requirement)

Tests run offline using mocks/moto - no real AWS required.

### View Coverage Report

```bash
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

## Docker

### Build and Run

```bash
# Backend
docker build -f Dockerfile -t mytraderpal-backend .
docker run -p 9000:8080 \
  -e TABLE_NAME=mtp_app \
  -e DEV_MODE=true \
  mytraderpal-backend

# Frontend
docker build -f infra/docker/Dockerfile.frontend -t mytraderpal-frontend .
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:9000 \
  mytraderpal-frontend

# Or use docker-compose
docker-compose up
```

## CI/CD Pipeline

The project includes a GitHub Actions CI/CD pipeline (`.github/workflows/ci.yml`) that:

1. **Tests Backend**: Runs pytest with coverage (fails if < 70%)
2. **Tests Frontend**: Lints and builds Next.js app
3. **Builds Docker Images**: Creates container images
4. **Deploys** (main branch only): Deploys CDK stack to AWS

### Setup CI/CD

1. Add GitHub Secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION` (optional, defaults to us-east-1)
   - `NEXT_PUBLIC_API_URL` (for frontend build)
   - `NEXT_PUBLIC_USER_POOL_ID`
   - `NEXT_PUBLIC_USER_POOL_CLIENT_ID`

2. Push to `main` branch to trigger deployment

## Monitoring

### Health Check

**Endpoint**: `GET /v1/health`

Returns comprehensive health status including metrics, environment info, and uptime.

### Metrics

**Endpoint**: `GET /v1/metrics`

Exposes Prometheus-formatted metrics:
- `requests_total`: Total requests
- `errors_total`: Total errors
- `request_latency_seconds_avg`: Average latency
- `uptime_seconds`: Application uptime
- `error_rate`: Error rate (0.0-1.0)

### Prometheus Setup

```bash
# Run Prometheus
docker run -p 9090:9090 \
  -v $(pwd)/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Access Prometheus UI
open http://localhost:9090
```

## Deploy

### Manual Deployment

```bash
cd infra/cdk
npm install
cdk synth
cdk bootstrap  # First time only
cdk deploy MyTraderPalStack
```

Find API URL and Cognito IDs in CDK outputs.

### Automated Deployment

Deployment happens automatically via CI/CD when pushing to `main` branch (after all tests pass).

## API Summary

- `GET /v1/health` - Health check with metrics
- `GET /v1/metrics` - Prometheus metrics
- **Notes:** `POST /v1/notes`, `GET /v1/notes`, `GET /v1/notes/{id}`, `PATCH /v1/notes/{id}`, `DELETE /v1/notes/{id}`
- **Strategies:** `POST /v1/strategies`, `GET /v1/strategies`, `GET /v1/strategies/{id}`, `PATCH /v1/strategies/{id}`, `DELETE /v1/strategies/{id}`
- **Reporting:** `GET /v1/reports/notes-summary?from=&to=&limit=`

**Auth:** Dev header `X-MTP-Dev-User` vs production JWT (Cognito authorizer)

## Design Notes

- **Layered Architecture**: API → Services → Repositories
- **SOLID Principles**: Single Responsibility, Dependency Inversion
- Single-table DynamoDB with GSI1 for queries
- Idempotent writes, pagination, UTC timestamps
- Comprehensive monitoring and metrics
- 84% test coverage with offline testing

## Documentation

- **[SDLC.md](docs/SDLC.md)**: Software Development Life Cycle model explanation
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Architecture diagrams and design decisions
- **[REPORT.md](docs/REPORT.md)**: Assignment 2 improvements report

## Troubleshooting

**Common Issues:**
- **Venv activation:** Use correct path for your OS
- **Missing AWS creds:** Only needed for deployment, not testing
- **CORS errors:** Check Origin header in requests
- **Coverage below 70%:** CI pipeline will fail - ensure all tests pass
- **Docker build fails:** Check Dockerfile paths and dependencies
- **Import errors:** Ensure `src/` is in Python path

**Reset environment:** Clear `.env` files and restart services.

## License

MIT
