# Fix for "Auth UserPool not configured" Error

## Problem

When running the frontend in Docker with hot reloading, you get:
```
⚠️  Cognito UserPool not configured. Authentication features will not work.
```

## Root Cause

Vite needs environment variables to be available in two ways:
1. **In the container process environment** - so Vite can read them via `process.env`
2. **In a `.env` file in the project root** - so Vite can read them at startup

When using Docker, the `.env` file needs to be:
- Loaded into the container's environment (via `env_file`)
- Mounted as a volume so Vite can read it directly

## Solution

Updated `docker-compose.dev.yml` to:

1. **Load `.env` file into container environment**:
   ```yaml
   env_file:
     - ./src/frontend-react/.env
   ```

2. **Mount `.env` file as volume**:
   ```yaml
   volumes:
     - ./src/frontend-react/.env:/app/.env
   ```

3. **Pass environment variables** (with fallbacks):
   ```yaml
   environment:
     - VITE_API_URL=${VITE_API_URL:-http://localhost:9000}
     - VITE_USER_POOL_ID=${VITE_USER_POOL_ID:-}
     - VITE_USER_POOL_CLIENT_ID=${VITE_USER_POOL_CLIENT_ID:-}
     - VITE_AWS_REGION=${VITE_AWS_REGION:-us-east-1}
   ```

## How It Works

1. **`env_file`** loads variables from `.env` into the container's process environment
2. **Volume mount** makes the `.env` file available at `/app/.env` for Vite to read
3. **`environment`** section allows overriding from shell environment if needed

Vite will read variables from:
- Process environment (via `env_file`)
- `.env` file in project root (via volume mount)
- Both sources are checked, so it works either way

## Your `.env` File Format

Make sure `src/frontend-react/.env` contains:

```env
VITE_API_URL=http://localhost:9000
VITE_USER_POOL_ID=us-east-1_EVFFPiYdF
VITE_USER_POOL_CLIENT_ID=67tnj8o8e9ds2ifsmaf1etk5ke
VITE_AWS_REGION=us-east-1
```

## Apply the Fix

### Option 1: Restart Frontend Container

```bash
docker-compose -f docker-compose.dev.yml restart frontend
```

### Option 2: Rebuild and Start

```bash
docker-compose -f docker-compose.dev.yml up --build frontend
```

### Option 3: Full Rebuild

```bash
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up --build
```

## Verify It Works

1. **Check container logs**:
   ```bash
   docker-compose -f docker-compose.dev.yml logs frontend
   ```

2. **Check environment variables in container**:
   ```bash
   docker-compose -f docker-compose.dev.yml exec frontend env | grep VITE
   ```

3. **Open browser console**:
   - Should NOT see "Auth UserPool not configured" warning
   - Authentication should work

## Troubleshooting

### Still Getting the Error?

1. **Verify `.env` file exists**:
   ```bash
   ls -la src/frontend-react/.env
   cat src/frontend-react/.env
   ```

2. **Check file format**:
   - No spaces around `=`
   - No quotes needed
   - Each variable on its own line

3. **Restart container**:
   ```bash
   docker-compose -f docker-compose.dev.yml restart frontend
   ```

4. **Check container environment**:
   ```bash
   docker-compose -f docker-compose.dev.yml exec frontend printenv | grep VITE
   ```

5. **Check if `.env` file is mounted**:
   ```bash
   docker-compose -f docker-compose.dev.yml exec frontend ls -la /app/.env
   ```

### Variables Not Loading?

- Make sure `.env` file is in `src/frontend-react/` directory
- Restart the container after changing `.env` file
- Vite reads `.env` at startup, so changes require a restart

## Summary

✅ **Fixed**: `.env` file is now properly loaded via `env_file` and mounted as volume
✅ **Result**: Vite can read environment variables from both sources
✅ **Action**: Restart the frontend container to apply changes

The authentication should now work correctly! 🎉


