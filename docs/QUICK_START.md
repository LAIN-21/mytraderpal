# Quick Start Guide - Run Everything at Once

## 🚀 One-Command Start

### Option 1: Using the Script (Recommended)

```bash
./scripts/run_local.sh
```

This will:
- ✅ Check Docker is running
- ✅ Build both backend and frontend Docker images
- ✅ Start all services
- ✅ Show you the URLs

### Option 2: Using Docker Compose Directly

```bash
docker-compose up --build
```

Or if you have newer Docker:
```bash
docker compose up --build
```

### Option 3: Run in Background (Detached Mode)

```bash
docker-compose up --build -d
```

## 📍 Access Your Application

Once started, access:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:9000
- **Health Check**: http://localhost:9000/v1/health
- **Metrics**: http://localhost:9000/v1/metrics

## 🔧 Prerequisites

1. **Docker Desktop** must be installed and running
2. **Environment Variables** (optional for local dev):
   - Create `src/frontend-react/.env` if you need Cognito auth:
     ```env
     VITE_API_URL=http://localhost:9000
     VITE_USER_POOL_ID=your-pool-id
     VITE_USER_POOL_CLIENT_ID=your-client-id
     VITE_AWS_REGION=us-east-1
     ```

## 🛠️ Useful Commands

### View Logs
```bash
docker-compose logs -f
```

### View Backend Logs Only
```bash
docker-compose logs -f api
```

### View Frontend Logs Only
```bash
docker-compose logs -f frontend
```

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Volumes
```bash
docker-compose down -v
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild and Restart
```bash
docker-compose up --build --force-recreate
```

## 🐛 Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

```bash
# Check what's using the ports
lsof -i :3000  # Frontend
lsof -i :9000  # Backend

# Stop the services
docker-compose down

# Or change ports in docker-compose.yml
```

### Docker Not Running

```bash
# Start Docker Desktop, then:
docker info  # Verify it's running
```

### Build Errors

```bash
# Clean build (removes cache)
docker-compose build --no-cache

# Then start
docker-compose up
```

### Frontend Can't Connect to Backend

The frontend is configured to connect to `http://api:9000` (internal Docker network).

If you're accessing from browser, it should work automatically. If not:
- Check that both services are running: `docker-compose ps`
- Check logs: `docker-compose logs frontend`

## 📝 What Gets Started

1. **Backend (API)**
   - Lambda function running in Docker
   - Port: 9000
   - Environment: DEV_MODE=true (bypasses auth for testing)

2. **Frontend (React App)**
   - Vite-built React app served by Nginx
   - Port: 3000
   - Connects to backend at http://api:9000

## 🎯 Development Workflow

1. **Start everything**:
   ```bash
   ./scripts/run_local.sh
   ```

2. **Make code changes**:
   - Backend: Changes require rebuild (`docker-compose up --build`)
   - Frontend: For hot reload, use `npm run dev` instead of Docker

3. **View logs**:
   ```bash
   docker-compose logs -f
   ```

4. **Stop when done**:
   ```bash
   docker-compose down
   ```

## 💡 Pro Tips

### Faster Development

For frontend development with hot reload:
```bash
# Terminal 1: Start backend only
docker-compose up api

# Terminal 2: Start frontend dev server
cd src/frontend-react
npm run dev
```

### Test Backend Only

```bash
# Start just the backend
docker-compose up api

# Test it
curl http://localhost:9000/v1/health
```

### Clean Slate

If something goes wrong:
```bash
# Stop everything
docker-compose down

# Remove all containers, networks, and volumes
docker-compose down -v

# Remove images (optional)
docker-compose down --rmi all

# Start fresh
docker-compose up --build
```


