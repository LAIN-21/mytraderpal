# Docker Troubleshooting Guide

## Issue: Docker Hanging on Image Pulls

If Docker is hanging when pulling base images (like `node:18-alpine` or `nginx:alpine`), try these solutions:

### Solution 1: Pull Images Separately First

```bash
# Pull base images before building
docker pull node:18-alpine
docker pull nginx:alpine
docker pull public.ecr.aws/lambda/python:3.11

# Then run docker-compose
docker-compose up --build
```

### Solution 2: Use the Fix Script

```bash
./scripts/fix_docker_hang.sh
docker-compose up --build
```

### Solution 3: Restart Docker Desktop

1. Quit Docker Desktop completely
2. Restart Docker Desktop
3. Wait for it to fully start
4. Try again: `docker-compose up --build`

### Solution 4: Clear Docker Build Cache

```bash
# Stop all containers
docker-compose down

# Prune build cache
docker builder prune -f

# Try again
docker-compose up --build
```

### Solution 5: Check Docker Network Settings

If you're behind a corporate firewall or VPN:

1. Open Docker Desktop → Settings → Resources → Network
2. Try disabling/enabling network features
3. Or configure proxy settings if needed

### Solution 6: Use Alternative Base Images (Temporary)

If the alpine images keep hanging, you can temporarily use non-alpine versions:

Edit `src/frontend-react/infra/docker/Dockerfile`:
```dockerfile
# Change from:
FROM node:18-alpine AS builder

# To:
FROM node:18-slim AS builder
```

And:
```dockerfile
# Change from:
FROM nginx:alpine

# To:
FROM nginx:latest
```

**Note**: This will create larger images but should pull faster.

### Solution 7: Build with No Cache

```bash
docker-compose build --no-cache
docker-compose up
```

### Solution 8: Check Docker Logs

```bash
# View Docker daemon logs
tail -f ~/Library/Containers/com.docker.docker/Data/log/host/Docker.log

# Or on Linux:
journalctl -u docker.service -f
```

### Solution 9: Increase Docker Resources

If Docker Desktop is low on resources:

1. Docker Desktop → Settings → Resources
2. Increase:
   - Memory (at least 4GB recommended)
   - CPUs (at least 2)
   - Disk image size

### Solution 10: Use Docker BuildKit

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Then build
docker-compose up --build
```

## Quick Fix Command

Run this to try multiple fixes at once:

```bash
# Stop everything
docker-compose down

# Pull images separately
docker pull node:18-alpine
docker pull nginx:alpine
docker pull public.ecr.aws/lambda/python:3.11

# Clear cache
docker builder prune -f

# Build with BuildKit
DOCKER_BUILDKIT=1 docker-compose up --build
```

## Still Having Issues?

1. **Check Docker is running**: `docker info`
2. **Check disk space**: `df -h` (Docker needs free space)
3. **Check network**: Try `ping docker.io`
4. **Restart Docker**: Quit and restart Docker Desktop
5. **Check Docker Desktop logs**: Help → Troubleshoot → View logs

## Alternative: Build Without Docker

If Docker keeps hanging, you can run locally without Docker:

### Backend Only (Lambda Local)
```bash
./scripts/dev_backend.sh
```

### Frontend Only (Vite Dev Server)
```bash
cd src/frontend-react
npm install
npm run dev
```

This won't use Docker but will let you develop locally.
