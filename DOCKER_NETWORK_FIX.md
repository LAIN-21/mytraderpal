# Docker Network Timeout Fix

## Problem

Docker is timing out when trying to pull images from Docker Hub:
```
failed to resolve source metadata for docker.io/library/node:18-slim: 
dial tcp 172.64.66.1:443: i/o timeout
```

This is a **network connectivity issue**, not an image problem.

## Quick Fixes

### Solution 1: Pull Images Separately First (Recommended)

```bash
# Use the script
./scripts/pull_images_first.sh

# Or manually
docker pull node:18-slim
docker pull nginx:latest
docker pull public.ecr.aws/lambda/python:3.11

# Then build
docker-compose up --build
```

### Solution 2: Restart Docker Desktop

1. Quit Docker Desktop completely
2. Wait 10 seconds
3. Restart Docker Desktop
4. Wait for it to fully start
5. Try again: `docker-compose up --build`

### Solution 3: Check Network/Firewall

```bash
# Test connectivity to Docker Hub
ping docker.io

# Test HTTPS connection
curl -I https://docker.io

# Check if behind VPN/firewall
# If yes, try disconnecting VPN temporarily
```

### Solution 4: Use Docker Desktop Network Settings

1. Docker Desktop → Settings → Resources → Network
2. Try disabling/enabling network features
3. Or reset network settings

### Solution 5: Configure Docker Registry Mirror

If Docker Hub is blocked/slow, use a mirror:

**macOS/Linux**: Create/edit `~/.docker/daemon.json`:
```json
{
  "registry-mirrors": [
    "https://mirror.gcr.io"
  ]
}
```

Then restart Docker.

### Solution 6: Use BuildKit with Better Error Handling

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Build with timeout settings
docker-compose build --progress=plain
```

### Solution 7: Build Offline (If You Have Images Cached)

```bash
# Check if images are already cached
docker images | grep -E "node|nginx|lambda"

# If cached, build without pulling
docker-compose build --pull=false
```

## Alternative: Run Without Docker

If Docker keeps timing out, you can run locally:

### Backend (Terminal 1)
```bash
./scripts/dev_backend.sh
```

### Frontend (Terminal 2)
```bash
cd src/frontend-react
npm install
npm run dev
```

This bypasses Docker entirely for local development.

## Network Troubleshooting

### Check Docker Network
```bash
docker network ls
docker network inspect bridge
```

### Check DNS
```bash
# macOS
scutil --dns

# Test DNS resolution
nslookup docker.io
```

### Check Proxy Settings
If you're behind a corporate proxy:
1. Docker Desktop → Settings → Resources → Proxies
2. Configure HTTP/HTTPS proxy
3. Add Docker Hub to no-proxy list if needed

## Most Likely Causes

1. **Slow/Unstable Internet**: Docker Hub can be slow
2. **VPN/Firewall**: Blocking Docker Hub access
3. **Corporate Network**: May block Docker Hub
4. **Docker Desktop Issues**: Network stack problems
5. **DNS Issues**: Can't resolve docker.io

## Quick Test

```bash
# Test if you can reach Docker Hub
curl -I https://registry-1.docker.io/v2/

# If this works, Docker should work too
# If this fails, it's a network/firewall issue
```

## Recommended Action

1. **First**: Try `./scripts/pull_images_first.sh` (pulls images separately)
2. **If that fails**: Restart Docker Desktop
3. **If still failing**: Check network/VPN/firewall
4. **Last resort**: Run without Docker for local dev

The script will retry failed pulls and give you better error messages.

