# Hot Reloading Setup

## ✅ Hot Reloading Enabled for Both Frontend and Backend!

Your development environment now supports automatic hot reloading for both services.

## 🚀 Quick Start

### Development Mode (with Hot Reload)

```bash
# Start with hot reloading
docker-compose -f docker-compose.dev.yml up --build

# Or in background
docker-compose -f docker-compose.dev.yml up -d
```

### Production Mode (no hot reload)

```bash
# Start production build
docker-compose up --build
```

## 📦 How It Works

### Frontend Hot Reload (Vite HMR)

**File**: `docker-compose.dev.yml`

- ✅ Uses Vite dev server instead of Nginx
- ✅ Source code mounted as volumes
- ✅ File changes trigger automatic browser refresh
- ✅ Fast HMR (Hot Module Replacement) for React components
- ✅ Polling enabled for Docker compatibility

**What gets reloaded automatically:**
- React components (`src/**/*.tsx`, `src/**/*.ts`)
- CSS files (`src/**/*.css`)
- Configuration files (`vite.config.ts`, `tailwind.config.js`, etc.)
- HTML template (`index.html`)

### Backend Hot Reload (Lambda)

**File**: `docker-compose.dev.yml`

- ✅ Source code mounted as volume
- ✅ Lambda RIE reloads code on each request
- ✅ No need to restart container for code changes
- ✅ Python modules reloaded automatically

**How it works:**
- Lambda Runtime Interface Emulator (RIE) loads code on each request
- With volume mounts, file changes are immediately available
- Next API request will use the updated code

## 📁 File Structure

```
.
├── docker-compose.yml          # Production (no hot reload)
├── docker-compose.dev.yml      # Development (with hot reload)
├── infra/docker/
│   ├── Dockerfile              # Production backend
│   └── Dockerfile.dev          # Development backend
└── src/frontend-react/infra/docker/
    ├── Dockerfile              # Production frontend
    └── Dockerfile.dev          # Development frontend
```

## 🔧 Configuration Details

### Frontend Development Dockerfile

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
EXPOSE 3000
CMD ["npm", "run", "dev"]  # Vite dev server with HMR
```

### Backend Development Dockerfile

```dockerfile
FROM public.ecr.aws/lambda/python:3.11
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt
COPY src/app ${LAMBDA_TASK_ROOT}
CMD [ "main.handler" ]  # Lambda RIE reloads on each request
```

### Volume Mounts

**Frontend:**
- `./src/frontend-react/src` → `/app/src` (source code)
- `./src/frontend-react/index.html` → `/app/index.html`
- `./src/frontend-react/.env` → `/app/.env` (environment variables for authentication)
- Config files mounted individually
- `node_modules` excluded (uses container's installed packages)

**Note**: The `.env` file contains your Cognito credentials (`VITE_USER_POOL_ID`, `VITE_USER_POOL_CLIENT_ID`, etc.). Vite reads this file at startup, so changes require a container restart.

**Backend:**
- `./src/app` → `/var/task` (Lambda handler code)
- `__pycache__` excluded (prevents conflicts)

## 🎯 Usage Examples

### Start Development Environment

```bash
# Start both services with hot reload
docker-compose -f docker-compose.dev.yml up
```

### Make Changes

1. **Edit frontend code** (`src/frontend-react/src/**/*.tsx`)
   - Save file
   - Browser automatically refreshes
   - Changes visible immediately

2. **Edit backend code** (`src/app/**/*.py`)
   - Save file
   - Make API request
   - New code is used automatically

### View Logs

```bash
# All services
docker-compose -f docker-compose.dev.yml logs -f

# Frontend only
docker-compose -f docker-compose.dev.yml logs -f frontend

# Backend only
docker-compose -f docker-compose.dev.yml logs -f api
```

### Stop Services

```bash
# Stop (keeps containers)
docker-compose -f docker-compose.dev.yml stop

# Stop and remove
docker-compose -f docker-compose.dev.yml down
```

## ⚡ Performance Tips

### Frontend

- **First load**: May take a few seconds (Vite compilation)
- **Subsequent changes**: Instant (HMR)
- **Large files**: May take 1-2 seconds to compile

### Backend

- **First request after change**: Uses new code immediately
- **No restart needed**: Lambda RIE handles reloading
- **Cold start**: First request may be slightly slower

## 🐛 Troubleshooting

### Frontend Not Reloading

**Symptoms**: Changes not reflected in browser

**Solutions**:
1. Check Vite is running: `docker-compose -f docker-compose.dev.yml logs frontend`
2. Verify volumes are mounted: `docker-compose -f docker-compose.dev.yml config`
3. Clear browser cache
4. Check file permissions
5. Restart: `docker-compose -f docker-compose.dev.yml restart frontend`

### Backend Not Reloading

**Symptoms**: API changes not taking effect

**Solutions**:
1. Verify volume mount: `docker-compose -f docker-compose.dev.yml config`
2. Check file was saved
3. Make a new API request (Lambda reloads on each request)
4. Check logs: `docker-compose -f docker-compose.dev.yml logs api`
5. Restart: `docker-compose -f docker-compose.dev.yml restart api`

### Port Already in Use

**Symptoms**: `Error: port 3000 is already in use`

**Solutions**:
```bash
# Find process using port
lsof -i :3000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.dev.yml
ports:
  - "3001:3000"  # Use 3001 instead
```

### Slow File Watching

**Symptoms**: Changes take long to detect

**Solutions**:
1. Already configured: `CHOKIDAR_USEPOLLING=true`
2. Increase polling interval (if needed)
3. Exclude large directories in `.dockerignore`

## 📊 Comparison

| Feature | Production (`docker-compose.yml`) | Development (`docker-compose.dev.yml`) |
|---------|-----------------------------------|----------------------------------------|
| Frontend | Nginx (static files) | Vite dev server (HMR) |
| Backend | Pre-built image | Volume mount (live reload) |
| Hot Reload | ❌ No | ✅ Yes |
| Build Time | Slower (full build) | Faster (dev server) |
| Image Size | Smaller (optimized) | Larger (dev tools) |
| Use Case | Production/Testing | Development |

## 🎉 Summary

✅ **Frontend**: Vite HMR with instant browser refresh
✅ **Backend**: Lambda RIE with automatic code reload
✅ **No Restarts**: Changes apply automatically
✅ **Fast Development**: Edit code and see changes immediately

**Start developing with hot reload:**
```bash
docker-compose -f docker-compose.dev.yml up --build
```

Happy coding! 🚀

