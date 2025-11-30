# MyTraderPal

A trading journal application for tracking trades, strategies, and market observations.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Complete Setup Guide](#-complete-setup-guide)
- [Architecture](#-architecture)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [CI/CD](#-cicd)
- [Troubleshooting](#-troubleshooting)

---

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

---

## 📚 Complete Setup Guide

This guide will walk you through setting up the project from scratch, including all required files, environment variables, and configurations.

### Prerequisites

Before you begin, ensure you have the following installed:

1. **Docker Desktop** (includes Docker and Docker Compose)
   - Download from: https://www.docker.com/products/docker-desktop
   - Verify: `docker --version` and `docker compose version`

2. **Make** (usually pre-installed on macOS/Linux)
   - Verify: `make --version`

3. **For AWS Deployment (Optional):**
   - **AWS CLI** - https://aws.amazon.com/cli/
   - **Terraform** >= 1.5.0 - https://www.terraform.io/downloads
   - **Git** - https://git-scm.com/downloads

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd mytraderpal
```

### Step 2: Create Environment Files

The project requires two `.env` files for local development. These files are **required** for Docker Compose to work correctly.

#### 2.1 Backend Environment File

**Location:** `src/app/.env`

**Create the file:**
```bash
# Copy from example template
cp src/app/.env.example src/app/.env
```

**Or create manually:**
```bash
cat > src/app/.env << 'EOF'
# MyTraderPal Backend Environment Variables

# DynamoDB Configuration
TABLE_NAME=mtp_app

# Development Mode
# Set to "true" to bypass Cognito authentication (for local development)
# Set to "false" for production (requires Cognito authentication)
DEV_MODE=true

# AWS Configuration
AWS_REGION=us-east-1

# AWS Credentials (Optional - for local development)
# If not set, Docker will try to use credentials from ~/.aws/credentials
# Or set these as environment variables before running docker-compose
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key
EOF
```

**Required Variables:**
- `TABLE_NAME` - DynamoDB table name (default: `mtp_app`)
- `DEV_MODE` - Set to `"true"` for local development (bypasses auth)
- `AWS_REGION` - AWS region (default: `us-east-1`)

**Optional Variables (for local AWS access):**
- `AWS_ACCESS_KEY_ID` - AWS access key (or use `~/.aws/credentials`)
- `AWS_SECRET_ACCESS_KEY` - AWS secret key (or use `~/.aws/credentials`)

#### 2.2 Frontend Environment File

**Location:** `src/frontend-react/.env`

**Create the file:**
```bash
# Copy from example template
cp src/frontend-react/.env.example src/frontend-react/.env
```

**Or create manually:**
```bash
cat > src/frontend-react/.env << 'EOF'
# MyTraderPal Frontend Environment Variables

# API Configuration
# Backend API URL (default: localhost for local development)
VITE_API_URL=http://localhost:9000

# AWS Cognito Configuration
# These are required for authentication in production
# For local development with DEV_MODE=true, these can be empty
VITE_USER_POOL_ID=
VITE_USER_POOL_CLIENT_ID=
VITE_AWS_REGION=us-east-1
EOF
```

**Required Variables:**
- `VITE_API_URL` - Backend API URL (default: `http://localhost:9000` for local dev)
- `VITE_AWS_REGION` - AWS region (default: `us-east-1`)

**Optional Variables (for production authentication):**
- `VITE_USER_POOL_ID` - Cognito User Pool ID (get from Terraform outputs)
- `VITE_USER_POOL_CLIENT_ID` - Cognito Client ID (get from Terraform outputs)

**Note:** All frontend environment variables **must** start with `VITE_` prefix (required by Vite).

### Step 3: Install Dependencies and Start

```bash
# Install dependencies and setup environment (creates .env files if missing)
make install

# Start the application
make start
```

The `make install` command will:
- Check prerequisites (Docker, Make)
- Create `.env` files from templates if they don't exist
- Prepare the environment

The `make start` command will:
- Build Docker images
- Start backend and frontend containers
- Make services available at:
  - Frontend: http://localhost:3000
  - Backend: http://localhost:9000

### Step 4: Verify Everything Works

```bash
# Check if services are running
make verify

# Test backend health endpoint
curl http://localhost:9000/v1/health

# View logs
make logs
```

---

## ☁️ AWS Setup (For Deployment)

If you want to deploy to AWS, follow these additional steps:

### Step 1: Configure AWS CLI

```bash
# Install AWS CLI (if not already installed)
# macOS: brew install awscli
# Linux: See https://aws.amazon.com/cli/

# Configure AWS credentials
aws configure

# You'll be prompted for:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format (json)

# Verify configuration
aws sts get-caller-identity
```

This creates `~/.aws/credentials` and `~/.aws/config` files.

### Step 2: Setup Terraform Remote State Backend

Terraform needs an S3 bucket and DynamoDB table for remote state management.

```bash
# Run the setup script
./scripts/setup-terraform-backend.sh
```

This script will:
- Create S3 bucket: `mytraderpal-terraform-state`
- Create DynamoDB table: `terraform-state-lock`
- Enable versioning and encryption
- Block public access

**Note:** The backend is already configured in `infra/terraform/main.tf`. The script just creates the required AWS resources.

### Step 3: Configure Terraform Variables

**Location:** `infra/terraform/terraform.tfvars`

**Create the file:**
```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
```

**Edit `terraform.tfvars` with your configuration:**
```hcl
# AWS Configuration
aws_region  = "us-east-1"
environment = "dev"

# DynamoDB
table_name = "mtp_app"

# Cognito
user_pool_name        = "mytraderpal-users"
cognito_domain_prefix = "mytraderpal-dev-UNIQUE"  # ⚠️ Must be globally unique!

# Cognito OAuth URLs
cognito_callback_urls = [
  "http://localhost:3000/login",
  "https://your-production-domain.com/login"
]

cognito_logout_urls = [
  "http://localhost:3000/",
  "https://your-production-domain.com/"
]

# Lambda
lambda_function_name = "mytraderpal-api"
lambda_handler       = "app.main.handler"
lambda_timeout       = 30

# API Gateway
api_name = "mytraderpal-api"

# Development Mode
dev_mode          = "true"   # Set to "false" for production
enable_cognito_auth = false  # Set to true when dev_mode is false

# CORS Configuration
cors_allowed_origins = [
  "http://localhost:3000",
  "https://your-production-domain.com"
]

cors_allowed_headers = [
  "Content-Type",
  "Authorization",
  "X-MTP-Dev-User"
]

cors_allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
```

**Important Notes:**
- `cognito_domain_prefix` must be **globally unique** across all AWS accounts
- Update `cognito_callback_urls` and `cors_allowed_origins` with your actual domains
- Set `dev_mode = "false"` and `enable_cognito_auth = true` for production

### Step 4: Initialize and Deploy Terraform

```bash
cd infra/terraform

# Initialize Terraform (downloads providers, sets up backend)
terraform init

# Review what will be created
terraform plan

# Apply changes (creates AWS resources)
terraform apply

# Get outputs (API URL, Cognito IDs, etc.)
terraform output
```

**Terraform Outputs:**
After deployment, Terraform will output:
- `api_url` - API Gateway URL (use in frontend `VITE_API_URL`)
- `user_pool_id` - Cognito User Pool ID (use in frontend `VITE_USER_POOL_ID`)
- `user_pool_client_id` - Cognito Client ID (use in frontend `VITE_USER_POOL_CLIENT_ID`)
- `cognito_domain` - Cognito domain name
- `table_name` - DynamoDB table name
- `lambda_function_name` - Lambda function name
- `ecr_repository_url` - ECR repository URL

**Update Frontend `.env` with Production Values:**
```bash
# After Terraform deployment, update frontend .env
cd ../../src/frontend-react
cat > .env << EOF
VITE_API_URL=https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com
VITE_USER_POOL_ID=$(cd ../../infra/terraform && terraform output -raw user_pool_id)
VITE_USER_POOL_CLIENT_ID=$(cd ../../infra/terraform && terraform output -raw user_pool_client_id)
VITE_AWS_REGION=us-east-1
EOF
```

---

## 🔐 GitHub Secrets Setup (For CI/CD)

If you want to enable automated deployment via GitHub Actions, you need to configure GitHub Secrets.

### Required GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add the following secrets:

1. **AWS_ACCESS_KEY_ID**
   - Your AWS access key ID
   - Get from: AWS Console → IAM → Users → Security credentials

2. **AWS_SECRET_ACCESS_KEY**
   - Your AWS secret access key
   - Get from: AWS Console → IAM → Users → Security credentials

3. **AWS_REGION** (optional, defaults to `us-east-1`)
   - AWS region for deployment
   - Example: `us-east-1`

4. **VITE_API_URL** (optional, for frontend build)
   - API Gateway URL
   - Get from: Terraform output `api_url`
   - Example: `https://xxxxx.execute-api.us-east-1.amazonaws.com`

5. **VITE_USER_POOL_ID** (optional, for frontend build)
   - Cognito User Pool ID
   - Get from: Terraform output `user_pool_id`

6. **VITE_USER_POOL_CLIENT_ID** (optional, for frontend build)
   - Cognito Client ID
   - Get from: Terraform output `user_pool_client_id`

7. **VITE_AWS_REGION** (optional, defaults to `us-east-1`)
   - AWS region for frontend
   - Example: `us-east-1`

8. **DEV_MODE** (optional, defaults to `false`)
   - Set to `"true"` for development, `"false"` for production
   - Example: `false`

### How CI/CD Works

1. **On Push to `main` branch:**
   - Tests run automatically (backend + frontend)
   - Docker images are built
   - Images are pushed to ECR
   - Terraform deploys infrastructure
   - Lambda function is updated with new image

2. **On Pull Request:**
   - Tests run automatically
   - No deployment (only validation)

**Note:** The CI/CD pipeline will automatically:
- Build Docker images
- Push to ECR
- Deploy with Terraform
- Handle existing resources (imports DynamoDB table if needed)

---

## 🏗️ Architecture

API Gateway → Lambda → DynamoDB with Cognito authentication. Infrastructure defined in Terraform.

**Modern Architecture:**
- Layered architecture (API → Services → Repositories)
- SOLID principles applied
- Comprehensive monitoring and metrics
- CI/CD pipeline with automated testing
- Docker containerization
- Health checks and Prometheus metrics

### Project Structure

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
│   │   ├── modules/        # Terraform modules
│   │   ├── main.tf         # Main configuration
│   │   ├── variables.tf    # Variable definitions
│   │   ├── outputs.tf     # Output values
│   │   └── terraform.tfvars.example  # Example config
│   └── docker/             # Docker files
│       ├── Dockerfile      # Backend Dockerfile
│       └── Dockerfile.prod # Production Dockerfile
├── scripts/                # Utility scripts
│   ├── setup-terraform-backend.sh  # Setup Terraform backend
│   ├── test.sh
│   ├── lint.sh
│   └── deploy.sh
├── .github/workflows/      # CI/CD pipelines
│   └── ci.yml
├── docker-compose.yml      # Local development
├── Makefile               # Development commands
├── requirements.txt       # Python dependencies
├── requirements-dev.txt   # Dev dependencies
└── README.md
```

---

## 💻 Development

### Local Development

**Option 1: Full Stack with Docker (Recommended)**

```bash
# Start both backend and frontend
make start

# Backend: http://localhost:9000
# Frontend: http://localhost:3000
```

**Option 2: Frontend Only (For UI Development)**

```bash
cd src/frontend-react
npm install
npm run dev
```

Visit `http://localhost:5173` (Vite default port)

**Option 3: Backend Testing**

```bash
# Test Lambda handler locally
python test_local.py

# Or use Docker Lambda runtime
./scripts/dev_backend.sh
```

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

### Make Commands

```bash
make install      # Install dependencies and setup environment
make start        # Start frontend and backend containers
make stop         # Stop all containers
make restart      # Restart all containers
make clean        # Stop containers and remove volumes
make verify       # Verify services are running
make logs         # View container logs

# Terraform commands
make terraform-init    # Initialize Terraform
make terraform-plan    # Plan infrastructure changes
make terraform-apply   # Apply infrastructure changes
make terraform-destroy # Destroy infrastructure
make terraform-output  # Show Terraform outputs
```

---

## 🧪 Testing

### Run Tests

```bash
python -m pytest tests/ \
  --cov=src/app \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-fail-under=70 \
  -v
```

**Coverage**: 79% (exceeds 70% requirement)

Tests run offline using mocks/moto - no real AWS required.

### View Coverage Report

```bash
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

---

## 🚀 Deployment

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

---

## 🔄 CI/CD Pipeline

The project includes a GitHub Actions CI/CD pipeline (`.github/workflows/ci.yml`) that:

1. **Tests Backend**: Runs pytest with coverage (fails if < 70%)
2. **Tests Frontend**: Lints and builds React app (Vite)
3. **Builds Docker Images**: Creates container images
4. **Deploys** (main branch only): Deploys infrastructure with Terraform to AWS

### Pipeline Jobs

- **test-backend**: Runs Python tests with coverage
- **test-frontend**: Builds and lints frontend
- **build-docker**: Builds Docker images for backend and frontend
- **deploy**: Deploys to AWS (only on `main` branch push)

### Setup CI/CD

1. Add GitHub Secrets (see [GitHub Secrets Setup](#-github-secrets-setup-for-cicd))
2. Push to `main` branch to trigger deployment

---

## 📊 Monitoring

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

---

## 📝 API Summary

- `GET /v1/health` - Health check with metrics
- `GET /v1/metrics` - Prometheus metrics
- **Notes:** `POST /v1/notes`, `GET /v1/notes`, `GET /v1/notes/{id}`, `PATCH /v1/notes/{id}`, `DELETE /v1/notes/{id}`
- **Strategies:** `POST /v1/strategies`, `GET /v1/strategies`, `GET /v1/strategies/{id}`, `PATCH /v1/strategies/{id}`, `DELETE /v1/strategies/{id}`
- **Reporting:** `GET /v1/reports/notes-summary?from=&to=&limit=`

**Auth:** Dev header `X-MTP-Dev-User` vs production JWT (Cognito authorizer)

---

## 🐛 Troubleshooting

### Common Issues

**Containers Won't Start**
```bash
# Check if ports are in use
lsof -i :3000  # Frontend port
lsof -i :9000  # Backend port

# Restart Docker Desktop
# Then try again: make start
```

**Missing .env Files**
```bash
# Create .env files from templates
make install
# Or manually:
cp src/app/.env.example src/app/.env
cp src/frontend-react/.env.example src/frontend-react/.env
```

**AWS Credentials Not Found**
```bash
# Configure AWS CLI
aws configure

# Verify
aws sts get-caller-identity
```

**Terraform Backend Error**
```bash
# Setup Terraform backend
./scripts/setup-terraform-backend.sh

# Then initialize
cd infra/terraform
terraform init
```

**Cognito Domain Already Exists**
- Cognito domain prefixes must be globally unique
- Change `cognito_domain_prefix` in `terraform.tfvars`
- Run `terraform apply` again

**Import Errors**
- Ensure `src/` is in Python path
- Check that all dependencies are installed

**Coverage Below 70%**
- CI pipeline will fail
- Ensure all tests pass
- Add tests for uncovered code

**Docker Build Fails**
- Check Dockerfile paths and dependencies
- Ensure Docker Desktop is running
- Try: `docker system prune -a` to clean up

**Reset Environment**
```bash
# Stop and clean everything
make clean

# Remove .env files (will be recreated on make install)
rm src/app/.env src/frontend-react/.env

# Start fresh
make install
make start
```

---

## 📚 Documentation

- **[SDLC.md](docs/SDLC.md)**: Software Development Life Cycle model explanation
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Architecture diagrams and design decisions
- **[REPORT.md](docs/REPORT.md)**: Assignment 2 improvements report
- **[infra/terraform/README.md](infra/terraform/README.md)**: Terraform infrastructure documentation

---

## 📋 Setup Checklist

Use this checklist when setting up the project for the first time:

### Local Development
- [ ] Docker Desktop installed and running
- [ ] Repository cloned
- [ ] `src/app/.env` created (from `.env.example`)
- [ ] `src/frontend-react/.env` created (from `.env.example`)
- [ ] `make install` completed successfully
- [ ] `make start` completed successfully
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend accessible at http://localhost:9000
- [ ] Health check works: `curl http://localhost:9000/v1/health`

### AWS Deployment (Optional)
- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] AWS credentials verified (`aws sts get-caller-identity`)
- [ ] Terraform installed (`terraform --version`)
- [ ] Terraform backend setup (`./scripts/setup-terraform-backend.sh`)
- [ ] `infra/terraform/terraform.tfvars` created and configured
- [ ] Terraform initialized (`terraform init`)
- [ ] Terraform plan reviewed (`terraform plan`)
- [ ] Infrastructure deployed (`terraform apply`)
- [ ] Terraform outputs saved (API URL, Cognito IDs)
- [ ] Frontend `.env` updated with production values

### CI/CD Setup (Optional)
- [ ] GitHub repository created
- [ ] GitHub Secrets configured:
  - [ ] `AWS_ACCESS_KEY_ID`
  - [ ] `AWS_SECRET_ACCESS_KEY`
  - [ ] `AWS_REGION` (optional)
  - [ ] `VITE_API_URL` (optional)
  - [ ] `VITE_USER_POOL_ID` (optional)
  - [ ] `VITE_USER_POOL_CLIENT_ID` (optional)
  - [ ] `VITE_AWS_REGION` (optional)
  - [ ] `DEV_MODE` (optional)
- [ ] CI/CD pipeline tested (push to `main` branch)

---

## 📄 License

MIT
