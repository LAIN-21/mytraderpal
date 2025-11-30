# Development to Deployment Process

This document explains how new features are developed and deployed in MyTraderPal.

## 📋 Overview

The application uses:
- **Docker** for local development and containerization
- **Terraform** for infrastructure as code (AWS resources)
- **GitHub Actions** for CI/CD automation
- **Lambda** for backend (serverless)
- **React + Vite** for frontend

## 🔄 Development Workflow

### 1. Local Development with Docker

#### Starting Development Environment

```bash
# One-command setup (first time)
make install

# Start all services
make start
```

**What happens:**
- Docker Compose builds images from `Dockerfile` files
- Backend: Lambda Runtime Interface Emulator (RIE) + HTTP proxy
- Frontend: Vite dev server with hot module replacement (HMR)
- Source code is mounted as volumes for **hot reloading**
- Services accessible at:
  - Frontend: http://localhost:3000
  - Backend: http://localhost:9000

#### Hot Reloading

**Backend (Lambda):**
- Source code mounted: `./src/app:/var/task/app`
- Lambda RIE reloads code on each request
- Changes to Python files are immediately available

**Frontend (React):**
- Source code mounted: `./src/frontend-react/src:/app/src`
- Vite HMR automatically reloads browser
- Changes to TypeScript/React files are immediately visible

#### Development Process

1. **Make code changes** in `src/app/` (backend) or `src/frontend-react/` (frontend)
2. **Changes are automatically picked up** (hot reload)
3. **Test locally** at http://localhost:3000
4. **No rebuild needed** - just save and refresh

### 2. Testing

```bash
# Run backend tests
pytest tests/ --cov=src/app --cov-fail-under=70

# Run frontend tests
cd src/frontend-react && npm test

# Or use CI locally
act  # (if you have GitHub Actions CLI)
```

## 🚀 Deployment Process

### Current Deployment Architecture

```
Developer Code
    ↓
GitHub Push (main branch)
    ↓
GitHub Actions CI/CD Pipeline
    ↓
├─→ Test Backend (pytest)
├─→ Test Frontend (npm test)
├─→ Build Docker Images
└─→ Deploy with Terraform
    ↓
AWS Infrastructure
    ├─→ Lambda Function (backend)
    ├─→ API Gateway
    ├─→ DynamoDB
    ├─→ Cognito
    └─→ (Frontend deployed separately - e.g., Amplify)
```

### Step-by-Step Deployment

#### Step 1: Code Changes & Testing

1. **Develop locally** with Docker
2. **Test changes** - ensure everything works
3. **Commit and push** to GitHub

```bash
git add .
git commit -m "Add new feature"
git push origin main
```

#### Step 2: CI/CD Pipeline (GitHub Actions)

**File:** `.github/workflows/ci.yml`

**Pipeline runs automatically on push to `main`:**

1. **Test Backend** (`test-backend` job)
   - Sets up Python 3.11
   - Installs dependencies from `requirements.txt`
   - Runs pytest with 70% coverage requirement
   - Uploads coverage to Codecov

2. **Test Frontend** (`test-frontend` job)
   - Sets up Node.js 18
   - Installs npm dependencies
   - Runs linter
   - Builds frontend (validates build works)

3. **Build Docker Images** (`build-docker` job)
   - Builds backend Docker image from `infra/docker/Dockerfile`
   - Builds frontend Docker image from `src/frontend-react/infra/docker/Dockerfile`
   - Validates images can be built
   - Uses GitHub Actions cache for faster builds

4. **Deploy** (`deploy` job) - **Only runs on `main` branch**
   - Configures AWS credentials
   - Sets up Terraform
   - Deploys infrastructure

#### Step 3: Build and Push Docker Image

**What Happens:**

1. **ECR Repository Created** (if it doesn't exist)
   - Terraform creates ECR repository for Lambda container images
   - Repository name: `mytraderpal-api-repo`

2. **Docker Image Built**
   - Uses production Dockerfile: `infra/docker/Dockerfile.prod`
   - Based on AWS Lambda Python 3.11 base image
   - Installs dependencies from `requirements.txt`
   - Copies application code from `src/app/`

3. **Image Pushed to ECR**
   - Tagged with commit SHA: `mytraderpal-api-repo:<sha>`
   - Also tagged as `latest`: `mytraderpal-api-repo:latest`
   - Pushed to AWS ECR

#### Step 4: Terraform Deployment

**What Terraform Does:**

1. **Creates/Updates AWS Resources**
   - **ECR Repository** - Container image registry
   - **DynamoDB Table** - Data storage
   - **Cognito User Pool** - Authentication
   - **Lambda Function** - Backend API (uses container image)
   - **API Gateway** - HTTP endpoint
   - **IAM Roles** - Permissions

2. **Configures Lambda Function**
   - Uses container image from ECR
   - Sets environment variables: `TABLE_NAME`, `DEV_MODE`, `AWS_REGION`
   - Configures handler: `app.main.handler`

**Terraform Files:**
- `infra/terraform/main.tf` - Main configuration
- `infra/terraform/modules/ecr/` - ECR repository
- `infra/terraform/modules/lambda/main.tf` - Lambda function (container image)
- `infra/terraform/terraform.tfvars` - Your configuration values

#### Step 5: Lambda Code Deployment

**How Lambda Code Gets Deployed:**

1. **Docker Image Built in CI/CD**:
   - Uses `infra/docker/Dockerfile.prod`
   - Builds production-ready container image
   - Includes all dependencies and application code

2. **Image Pushed to ECR**:
   - Pushed to ECR repository created by Terraform
   - Tagged with commit SHA and `latest`

3. **Terraform Updates Lambda**:
   - Lambda function uses `package_type = "Image"`
   - Points to ECR image URI
   - Only updates if image URI changes

**Key Benefit:** Same Docker image used in development (docker-compose) and production (Lambda)!

### Manual Deployment

If you need to deploy manually (without CI/CD):

```bash
# Option 1: Use Makefile
make deploy

# Option 2: Use deployment script
./scripts/deploy.sh

# Option 3: Manual Terraform
cd infra/terraform
terraform init
terraform plan
terraform apply
```

## 🔍 Key Differences: Development vs Production

### Development (Docker)

| Aspect | Development | Production |
|--------|------------|------------|
| **Backend** | Lambda RIE + HTTP Proxy | AWS Lambda |
| **Frontend** | Vite Dev Server | Static build (Nginx/Amplify) |
| **Hot Reload** | ✅ Yes | ❌ No |
| **Code Location** | Volume mounts | Packaged in image/ZIP |
| **Environment** | `.env` files | Terraform variables |
| **Port** | 9000 (proxy) | API Gateway URL |

### Code Packaging

**Development:**
- Code mounted as volumes
- Changes immediately available
- Uses `infra/docker/Dockerfile` (includes dev tools like proxy)

**Production:**
- **Backend:** Docker image built from `infra/docker/Dockerfile.prod` → Pushed to ECR → Lambda uses image
- **Frontend:** Vite builds → Static files → Deploy to hosting (e.g., Amplify)

## 📝 Adding a New Feature

### Example: Adding a New API Endpoint

1. **Develop Locally:**
   ```bash
   make start
   # Edit src/app/api/router.py
   # Add new handler in src/app/api/
   # Test at http://localhost:9000/v1/new-endpoint
   ```

2. **Test:**
   ```bash
   pytest tests/
   ```

3. **Commit & Push:**
   ```bash
   git add .
   git commit -m "Add new endpoint"
   git push origin main
   ```

4. **CI/CD Automatically:**
   - Tests run
   - If tests pass → Terraform deploys
   - Lambda function updated with new code
   - API Gateway routes updated (if needed)

5. **Verify Deployment:**
   ```bash
   # Get API URL from Terraform
   cd infra/terraform
   terraform output api_url
   
   # Test
   curl $(terraform output -raw api_url)/v1/new-endpoint
   ```

## 🔧 Configuration Management

### Development Environment Variables

**Backend:** `src/app/.env`
```env
TABLE_NAME=mtp_app
DEV_MODE=true
AWS_REGION=us-east-1
```

**Frontend:** `src/frontend-react/.env`
```env
VITE_API_URL=http://localhost:9000
VITE_USER_POOL_ID=...
VITE_USER_POOL_CLIENT_ID=...
```

### Production Environment Variables

**Managed by Terraform:**
- `infra/terraform/terraform.tfvars` - Your configuration
- `infra/terraform/main.tf` - Sets Lambda env vars
- Terraform outputs → Frontend config

## 🐛 Troubleshooting

### Changes Not Reflecting in Development

```bash
# Restart containers
make restart

# Check logs
make logs

# Verify volumes are mounted
docker-compose ps
```

### Deployment Issues

```bash
# Check Terraform state
cd infra/terraform
terraform plan

# Check Lambda function
aws lambda get-function --function-name mytraderpal-api

# View Lambda logs
aws logs tail /aws/lambda/mytraderpal-api --follow
```

## 📚 Related Documentation

- `docs/DOCKER_SETUP.md` - Docker configuration details
- `docs/DEPLOYMENT.md` - Deployment guide
- `infra/terraform/README.md` - Terraform documentation
- `README.md` - Quick start guide

## 🎯 Summary

**Development:**
1. `make start` → Docker Compose with hot reload
2. Edit code → Changes immediately visible
3. Test locally

**Deployment:**
1. Push to GitHub → CI/CD triggers
2. Tests run → Build Docker images (validation)
3. Terraform packages code → Deploys to AWS
4. Lambda function updated → API available

**Key Point:** Docker images are used for **both development and production**! The same Docker image built in CI/CD is pushed to ECR and used by Lambda, ensuring consistency between environments.

