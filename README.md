# MyTraderPal

A trading journal application for tracking trades, strategies, and market observations.

## 🚀 Quick Start

Get up and running in 2 commands:

```bash
# 1. Install dependencies and setup environment
make install

# 2. Start frontend and backend
make start
```

That's it! Your application will be running at:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:9000

### Prerequisites

- **Docker Desktop** installed and running
- **Make** (usually pre-installed on macOS/Linux)

### Verify Setup

```bash
# Check if everything is working
make verify

# View logs
make logs

# Stop containers
make stop
```

### Troubleshooting

If you encounter issues:
1. Ensure Docker Desktop is running
2. Check ports 3000 and 9000 are not in use
3. Run `make clean` to reset and try again

---

## What it does

Record daily trading notes with direction, session, and risk tracking. Create and manage trading strategies with market specifications. Generate reports on hit/miss performance and session analysis.

## Architecture

API Gateway → Lambda → DynamoDB with Cognito authentication. Infrastructure defined in Terraform.

**Modern Architecture:**
- Layered architecture (API → Services → Repositories)
- SOLID principles applied
- Comprehensive monitoring and metrics
- CI/CD pipeline with automated testing
- Docker containerization
- Health checks and Prometheus metrics

## Requirements

**For Quick Start (Recommended):**
- **Docker Desktop** (includes Docker and Docker Compose)
- **Make** (usually pre-installed)

**For Manual Setup:**
- **Python 3.11+** (backend)
- **Node.js 18+** (frontend)
- **AWS CLI** (for deployment)
- **Terraform** >= 1.5.0 (for infrastructure)

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
│   └── frontend-react/      # React frontend (Vite)
│       ├── src/
│       │   ├── components/
│       │   ├── lib/
│       │   └── pages/
│       └── package.json
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── infra/
│   ├── terraform/          # Terraform infrastructure
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

## Manual Setup (Alternative)

If you prefer not to use Docker, you can set up manually:

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
cd src/frontend-react
npm install
```

## Environment Variables

The project uses environment variables for both frontend and backend configuration.

### Backend Environment Variables

**Location:** `src/app/.env`

**Required variables:**
- `TABLE_NAME` - DynamoDB table name (default: `mtp_app`)
- `DEV_MODE` - Enable development mode to bypass auth (default: `true`)
- `AWS_REGION` - AWS region (default: `us-east-1`)

**Setup:**
```bash
# Copy template
cp src/app/.env.example src/app/.env

# Edit if needed (defaults work for local development)
```

### Frontend Environment Variables

**Location:** `src/frontend-react/.env`

**Required variables:**
- `VITE_API_URL` - Backend API URL (default: `http://localhost:9000`)
- `VITE_USER_POOL_ID` - Cognito User Pool ID (optional for dev mode)
- `VITE_USER_POOL_CLIENT_ID` - Cognito Client ID (optional for dev mode)
- `VITE_AWS_REGION` - AWS region (default: `us-east-1`)

**Setup:**
```bash
# Copy template
cp src/frontend-react/.env.example src/frontend-react/.env

# Edit with your Cognito values (optional for local dev)
```

**Note:** The `make install` command automatically creates both `.env` files from templates.

## Running

### Local Development

**Option 1: Frontend Only (Recommended for UI Development)**
```bash
# Quick start - frontend only
./scripts/dev_frontend.sh

# Or manually
cd src/frontend-react
npm install
npm run dev
```

Visit `http://localhost:5173` (Vite default port, points to deployed API or configure API URL)

**Option 2: Full Stack with Docker**

**Production Mode (no hot reload):**
```bash
# Start both backend and frontend
docker-compose up --build

# Backend: http://localhost:9000
# Frontend: http://localhost:3000
```

**Development Mode (with hot reload):**
```bash
# Start with hot reloading for both frontend and backend
docker-compose up --build

# Or use the script
./scripts/dev_hot_reload.sh

# Changes to code will automatically reload:
# - Frontend: Browser auto-refreshes on file changes
# - Backend: Code reloads on each API request
```

**Option 3: Backend Testing**
```bash
# Test Lambda handler locally
python test_local.py

# Or use Docker Lambda runtime
./scripts/dev_backend.sh
```

**Note**: The backend is a Lambda function, so it's designed for AWS deployment. For local development:
- Use `test_local.py` for quick testing
- Use Docker with Lambda runtime for full local testing
- Use `DEV_MODE=true` to bypass authentication
- Frontend can connect to deployed API for full-stack testing

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
cd src/frontend-react
docker build -f infra/docker/Dockerfile -t mytraderpal-frontend .
docker run -p 3000:80 \
  -e VITE_API_URL=http://localhost:9000 \
  mytraderpal-frontend

# Or use docker-compose
docker-compose up
```

## CI/CD Pipeline

The project includes a GitHub Actions CI/CD pipeline (`.github/workflows/ci.yml`) that:

1. **Tests Backend**: Runs pytest with coverage (fails if < 70%)
2. **Tests Frontend**: Lints and builds React app (Vite)
3. **Builds Docker Images**: Creates container images
4. **Deploys** (main branch only): Deploys infrastructure with Terraform to AWS

### Setup CI/CD

1. Add GitHub Secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION` (optional, defaults to us-east-1)
   - `VITE_API_URL` (for frontend build)
   - `VITE_USER_POOL_ID`
   - `VITE_USER_POOL_CLIENT_ID`

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

**Configuration**: `monitoring/prometheus.yml`

```bash
# Run Prometheus
docker run -p 9090:9090 \
  -v $(pwd)/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Access Prometheus UI
open http://localhost:9090
```

**Prometheus Configuration**:
- Scrapes metrics from `/v1/metrics` endpoint
- 15-second scrape interval
- Configured for local and production environments

### Grafana Setup

**Dashboard**: `monitoring/grafana-dashboard.json`

1. **Start Grafana**:
```bash
docker run -d -p 3001:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana
```

2. **Access Grafana**: `http://localhost:3001` (admin/admin)

3. **Configure Prometheus Data Source**:
   - Go to Configuration → Data Sources
   - Add Prometheus
   - URL: `http://host.docker.internal:9090` (or your Prometheus URL)

4. **Import Dashboard**:
   - Go to Dashboards → Import
   - Upload `monitoring/grafana-dashboard.json`
   - Select Prometheus as data source

**Dashboard Panels**:
- Request Rate (requests/second)
- Error Rate (errors/second)
- Average Latency (response time)
- Error Rate Percentage

## Deploy

### Manual Deployment

```bash
# Deploy infrastructure with Terraform
make deploy

# Or manually:
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your configuration
terraform init
terraform plan
terraform apply
```

Get API URL and Cognito IDs from Terraform outputs:
```bash
terraform output
```

### Automated Deployment

Deployment happens automatically via CI/CD when pushing to `main` branch (after all tests pass). The pipeline uses Terraform to deploy infrastructure.

### Terraform Commands

```bash
make terraform-init    # Initialize Terraform
make terraform-plan    # Plan changes
make terraform-apply   # Apply changes
make terraform-output  # Show outputs
make terraform-destroy # Destroy infrastructure (careful!)
```

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
