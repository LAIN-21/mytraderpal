# What is Alpine Linux?

## What is Alpine?

**Alpine Linux** is a minimal, security-oriented Linux distribution designed for:
- **Small size**: Base image is only ~5MB (vs ~100MB+ for standard images)
- **Security**: Uses musl libc and focuses on security
- **Speed**: Faster to pull and deploy

## Why Use Alpine in Docker?

### Benefits:
1. **Smaller Images**: 
   - `node:18-alpine` ≈ 50MB
   - `node:18` (standard) ≈ 350MB
   - `nginx:alpine` ≈ 25MB
   - `nginx:latest` ≈ 150MB

2. **Faster Builds**: Less to download = faster builds
3. **Lower Costs**: Smaller images = less storage/bandwidth
4. **Security**: Minimal attack surface

### Trade-offs:
- Sometimes slower package installation (musl vs glibc)
- Can have compatibility issues with some packages
- Network issues can cause hangs (like you're experiencing)

## Current Issue: Hanging on Pull

Docker is hanging when trying to pull:
- `node:18-alpine`
- `nginx:alpine`

This is usually caused by:
1. **Network issues** (slow connection, firewall, VPN)
2. **Docker registry problems** (Docker Hub rate limiting)
3. **DNS issues**
4. **Docker daemon issues**

## Solutions

### Solution 1: Use Non-Alpine Images (Quickest Fix)

Replace Alpine with standard images - they're more reliable but larger:

**Frontend Dockerfile** - Change from:
```dockerfile
FROM node:18-alpine AS builder
...
FROM nginx:alpine
```

**To:**
```dockerfile
FROM node:18-slim AS builder
...
FROM nginx:latest
```

**Pros**: More reliable, better compatibility
**Cons**: Larger images (~3x bigger)

### Solution 2: Pull Images Separately First

```bash
# Pull images before building
docker pull node:18-alpine
docker pull nginx:alpine

# Then build
docker-compose up --build
```

### Solution 3: Use Alternative Registries

If Docker Hub is slow, use alternative registries:
- GitHub Container Registry (ghcr.io)
- AWS ECR Public Gallery
- Quay.io

### Solution 4: Fix Network Issues

```bash
# Check Docker network
docker info | grep -i network

# Restart Docker daemon
# macOS: Restart Docker Desktop
# Linux: sudo systemctl restart docker

# Check DNS
ping docker.io
```

### Solution 5: Use BuildKit with Better Caching

```bash
DOCKER_BUILDKIT=1 docker-compose build
```

## Recommendation

For your use case, I recommend **Solution 1** (use non-Alpine) because:
- More reliable (less hanging)
- Better compatibility
- Still reasonable size
- Faster to get working

The size difference (50MB vs 150MB) is negligible for most deployments.

