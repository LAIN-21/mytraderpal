# Local Development Testing Guide

Quick guide to verify local development is working.

## Prerequisites Check

```bash
# Check Docker is running
docker info

# Check Make is available
make --version
```

## Step-by-Step Setup

### 1. Install and Setup Environment

```bash
make install
```

**What this does:**
- ✅ Checks Docker is installed and running
- ✅ Creates `src/app/.env` from template (backend)
- ✅ Creates `src/frontend-react/.env` from template (frontend)
- ✅ Validates prerequisites

**Expected output:**
```
🔍 Checking prerequisites...
✅ Prerequisites check passed
📝 Setting up environment files...
✅ Created src/app/.env from template (backend)
✅ Created src/frontend-react/.env from template
✅ Installation complete!
```

### 2. Start Services

```bash
make start
```

**What this does:**
- ✅ Builds Docker images (installs dependencies)
- ✅ Starts backend container (port 9000)
- ✅ Starts frontend container (port 3000)
- ✅ Sets up hot reloading

**Expected output:**
```
🚀 Starting MyTraderPal...
⏳ Waiting for services to be ready...
✅ Services started!

📍 Access your application:
   Frontend: http://localhost:3000
   Backend:  http://localhost:9000
   Health:   http://localhost:9000/v1/health
```

### 3. Verify Services

```bash
make verify
```

**What this does:**
- ✅ Checks containers are running
- ✅ Tests backend health endpoint
- ✅ Tests frontend accessibility

**Expected output:**
```
🔍 Verifying services...
✅ Containers are running
Testing endpoints...
✅ Backend health check passed
✅ Frontend is accessible
```

### 4. Manual Testing

#### Test Backend Health Endpoint

```bash
curl http://localhost:9000/v1/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-30T...",
  "uptime_seconds": 123,
  "environment": {
    "table_name": "mtp_app",
    "dev_mode": true
  }
}
```

#### Test Backend Metrics

```bash
curl http://localhost:9000/v1/metrics
```

**Expected response:** Prometheus-formatted metrics

#### Test Frontend

Open in browser:
```
http://localhost:3000
```

**Expected:** React app loads successfully

### 5. View Logs (Optional)

```bash
make logs
```

Or view specific service:
```bash
docker-compose logs -f api      # Backend logs
docker-compose logs -f frontend # Frontend logs
```

### 6. Stop Services

```bash
make stop
```

Or clean everything:
```bash
make clean  # Stops and removes volumes
```

## Quick Test Script

Run all tests at once:

```bash
# Full test sequence
make install && \
make start && \
sleep 10 && \
make verify && \
curl -s http://localhost:9000/v1/health | jq . && \
echo "✅ All tests passed!"
```

## Troubleshooting

### Containers won't start

```bash
# Check if ports are in use
lsof -i :3000
lsof -i :9000

# Check Docker is running
docker ps

# View error logs
make logs
```

### Backend health check fails

```bash
# Check backend logs
docker-compose logs api

# Restart backend
docker-compose restart api
```

### Frontend not loading

```bash
# Check frontend logs
docker-compose logs frontend

# Verify .env file exists
cat src/frontend-react/.env

# Restart frontend
docker-compose restart frontend
```

### Environment variables missing

```bash
# Recreate .env files
make install

# Or manually
cp src/app/.env.example src/app/.env
cp src/frontend-react/.env.example src/frontend-react/.env
```

## Expected File Structure

After `make install`, you should have:

```
mytraderpal/
├── src/
│   ├── app/
│   │   └── .env          ✅ Created
│   └── frontend-react/
│       └── .env          ✅ Created
```

## Success Criteria

✅ `make install` completes without errors  
✅ `make start` shows "Services started!"  
✅ `make verify` shows all checks passing  
✅ `curl http://localhost:9000/v1/health` returns JSON  
✅ Browser opens `http://localhost:3000` successfully  

## Next Steps

Once local development is verified:

1. **Test API endpoints:**
   ```bash
   curl -X POST http://localhost:9000/v1/notes \
     -H "Content-Type: application/json" \
     -H "X-MTP-Dev-User: test-user" \
     -d '{"date":"2025-11-30","text":"Test note"}'
   ```

2. **Test frontend features:**
   - Navigate to http://localhost:3000
   - Try creating a note
   - Try creating a strategy

3. **Verify hot reloading:**
   - Edit a file in `src/app/` → Backend reloads on next request
   - Edit a file in `src/frontend-react/src/` → Browser auto-refreshes

