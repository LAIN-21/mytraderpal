# Docker Containerization Setup

## ✅ All Services Containerized

Your entire application is fully containerized with Docker!

## 📦 Containerized Services

### 1. Backend API (Lambda)

**Dockerfile**: `infra/docker/Dockerfile`

```dockerfile
FROM public.ecr.aws/lambda/python:3.11
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt
COPY src/app ${LAMBDA_TASK_ROOT}
CMD [ "main.handler" ]
```

**Features**:
- ✅ Uses official AWS Lambda Python 3.11 base image
- ✅ Installs dependencies from `requirements.txt`
- ✅ Copies application code from `src/app`
- ✅ Configured for Lambda runtime
- ✅ Exposes port 8080 (Lambda default)

### 2. Frontend (React + Vite)

**Dockerfile**: `src/frontend-react/infra/docker/Dockerfile`

```dockerfile
# Multi-stage build
FROM node:18-alpine AS builder
# ... build steps ...
FROM nginx:alpine
# ... production setup ...
```

**Features**:
- ✅ Multi-stage build (optimized image size)
- ✅ Builds React app with Vite
- ✅ Serves with Nginx
- ✅ SPA routing configured
- ✅ Exposes port 80

## 🐳 Docker Compose

**File**: `docker-compose.yml` (root level)

**Services**:
1. **api** - Backend Lambda function
2. **frontend** - React frontend

**Features**:
- ✅ Both services configured
- ✅ Environment variables set
- ✅ Port mappings correct
- ✅ Service dependencies (frontend depends on api)
- ✅ Build args for frontend

## 🚀 Running Everything

### Quick Start

```bash
# Start all services
docker-compose up --build

# Or use the script
./scripts/run_local.sh
```

### Individual Services

```bash
# Backend only
docker-compose up api

# Frontend only
docker-compose up frontend
```

### Background Mode

```bash
docker-compose up -d
```

## 📍 Access Points

Once running:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:9000
- **Health Check**: http://localhost:9000/v1/health
- **Metrics**: http://localhost:9000/v1/metrics

## 🔧 Build Commands

### Build Individual Images

```bash
# Backend
docker build -f infra/docker/Dockerfile -t mytraderpal-backend .

# Frontend
cd src/frontend-react
docker build -f infra/docker/Dockerfile -t mytraderpal-frontend .
```

### Build with Docker Compose

```bash
# Build all services
docker-compose build

# Rebuild without cache
docker-compose build --no-cache

# Build specific service
docker-compose build api
docker-compose build frontend
```

## 📝 Environment Variables

### Backend (in docker-compose.yml)

```yaml
environment:
  - TABLE_NAME=mtp_app
  - DEV_MODE=true
  - AWS_REGION=us-east-1
```

### Frontend (build args)

```yaml
build:
  args:
    - VITE_API_URL=http://api:9000
    - VITE_USER_POOL_ID=${VITE_USER_POOL_ID:-}
    - VITE_USER_POOL_CLIENT_ID=${VITE_USER_POOL_CLIENT_ID:-}
    - VITE_AWS_REGION=${VITE_AWS_REGION:-us-east-1}
```

## 🛠️ Useful Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f frontend
```

### Stop Services

```bash
# Stop (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart api
```

### Clean Up

```bash
# Remove containers, networks, volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Prune everything
docker system prune -a
```

## ✅ Verification Checklist

- [x] Backend Dockerfile exists and builds
- [x] Frontend Dockerfile exists and builds
- [x] Docker Compose configured
- [x] Environment variables set
- [x] Port mappings correct
- [x] Service dependencies configured
- [x] .dockerignore files present
- [x] Multi-stage build for frontend
- [x] CI/CD builds Docker images

## 🎯 Production Readiness

### Backend
- ✅ Optimized Lambda base image
- ✅ Minimal dependencies
- ✅ Proper handler configuration
- ✅ Environment variables configurable

### Frontend
- ✅ Multi-stage build (smaller image)
- ✅ Production-ready Nginx
- ✅ SPA routing configured
- ✅ Build-time environment variables

## 📊 Image Sizes

Expected sizes:
- **Backend**: ~200-300 MB (Lambda base image)
- **Frontend**: ~50-100 MB (Nginx Alpine + built assets)

## 🔒 Security

- ✅ No secrets in Dockerfiles
- ✅ Environment variables via build args
- ✅ .dockerignore excludes sensitive files
- ✅ Minimal base images (Alpine)

## 🚀 Deployment

Docker images are built in CI/CD pipeline:
- Backend: Built for Lambda deployment
- Frontend: Built for static hosting or container deployment

Both images are ready for:
- AWS Lambda (backend)
- AWS ECS/Fargate
- Any container platform
- Static hosting (frontend)

