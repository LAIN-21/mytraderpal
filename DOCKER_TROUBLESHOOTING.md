# Docker Troubleshooting Guide

## Issue: Frontend Build Stuck

### Problem
Docker build hangs when building the frontend, especially at "loading metadata" step.

### Solutions

#### Solution 1: Use Development Mode (Recommended for Local Dev)

```bash
# Use the development docker-compose (faster, no build step)
docker-compose -f docker-compose.dev.yml up

# Or just run frontend locally (even faster)
cd src/frontend && npm run dev
```

#### Solution 2: Fix Production Build

The issue was with Next.js standalone output. I've fixed it:

1. **Stop current build:**
   ```bash
   docker-compose down
   docker system prune -f  # Optional: clean up
   ```

2. **Rebuild with fixed Dockerfile:**
   ```bash
   docker-compose build --no-cache frontend
   docker-compose up
   ```

#### Solution 3: Build Frontend Separately

```bash
# Build frontend image separately to see errors
docker build -f infra/docker/Dockerfile.frontend -t mytraderpal-frontend .

# If it hangs, try with more verbose output
docker build --progress=plain -f infra/docker/Dockerfile.frontend -t mytraderpal-frontend .
```

#### Solution 4: Skip Frontend in Docker (Fastest for Development)

```bash
# Run only backend in Docker
docker-compose up api

# Run frontend locally in another terminal
cd src/frontend
npm install
npm run dev
```

## Common Issues

### 1. Network Issues Pulling Images

```bash
# Check Docker network
docker network ls

# Try pulling image manually
docker pull node:18-alpine

# If still stuck, use different registry or mirror
```

### 2. Build Context Too Large

```bash
# Check .dockerignore exists
cat .dockerignore

# Ensure node_modules is ignored
echo "node_modules/" >> .dockerignore
echo ".next/" >> .dockerignore
```

### 3. Out of Disk Space

```bash
# Check disk space
docker system df

# Clean up
docker system prune -a
```

### 4. Environment Variables Not Set

The build might hang if required env vars are missing. Use defaults:

```bash
# Set defaults in .env file
NEXT_PUBLIC_USER_POOL_ID=test
NEXT_PUBLIC_USER_POOL_CLIENT_ID=test
NEXT_PUBLIC_AWS_REGION=us-east-1
```

## Quick Fixes

### For Development (Fastest)

```bash
# Option 1: Frontend only (recommended)
cd src/frontend && npm run dev

# Option 2: Backend in Docker, frontend local
docker-compose up api
# In another terminal:
cd src/frontend && npm run dev
```

### For Production Build

```bash
# Clean build
docker-compose down
docker-compose build --no-cache
docker-compose up
```

## Recommended Development Setup

**Best approach for local development:**

1. **Terminal 1 - Backend (if needed):**
   ```bash
   docker-compose up api
   # Or use: ./scripts/dev_backend.sh
   ```

2. **Terminal 2 - Frontend:**
   ```bash
   cd src/frontend
   npm install
   npm run dev
   ```

This avoids Docker build issues and gives you hot reload!

