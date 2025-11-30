# Authentication DEV_MODE Fix

## Problem

When trying to save a strategy (or any API call), you got:
```
Failed to save strategy: Authentication required
```

## Root Cause

1. **Backend** is in `DEV_MODE=true` (set in `docker-compose.yml`)
2. **Backend** accepts `X-MTP-Dev-User` header when `DEV_MODE=true`
3. **Frontend** API client always tried to get a Cognito token
4. **Cognito** is not configured (no `VITE_USER_POOL_ID` or `VITE_USER_POOL_CLIENT_ID`)
5. **Frontend** failed to get token and threw "Authentication required" error
6. **Frontend** never sent the `X-MTP-Dev-User` header that the backend expects

## Solution

Updated `src/frontend-react/src/lib/api-client.ts` to:

1. **Check if Cognito is configured** before trying to authenticate
2. **Use DEV_MODE header** (`X-MTP-Dev-User: dev-user`) when Cognito is not configured
3. **Fall back to DEV_MODE** if Cognito auth fails in development mode
4. **Use Cognito token** when Cognito is properly configured

## How It Works Now

### When Cognito is NOT configured (Development):

```typescript
// API client detects no Cognito config
// Sends: X-MTP-Dev-User: dev-user
// Backend accepts it because DEV_MODE=true
```

### When Cognito IS configured (Production):

```typescript
// API client gets Cognito token
// Sends: Authorization: Bearer <token>
// Backend validates token via API Gateway authorizer
```

## Testing

### 1. Rebuild Frontend

Since the frontend is containerized, you need to rebuild:

```bash
# Rebuild just the frontend
docker-compose build frontend

# Or rebuild everything
docker-compose up --build
```

### 2. Test API Calls

1. Open `http://localhost:3000` in browser
2. Try to create a strategy or note
3. Should work without authentication errors
4. Check browser DevTools → Network tab
5. Verify requests include `X-MTP-Dev-User: dev-user` header

### 3. Verify Backend Logs

```bash
# Check backend logs
docker-compose logs api

# Should see successful requests with dev-user
```

## Configuration

### Current Setup (Development)

**docker-compose.yml**:
```yaml
api:
  environment:
    - DEV_MODE=true  # ✅ Enables dev mode

frontend:
  build:
    args:
      - VITE_USER_POOL_ID=${VITE_USER_POOL_ID:-}  # Empty = not configured
      - VITE_USER_POOL_CLIENT_ID=${VITE_USER_POOL_CLIENT_ID:-}  # Empty = not configured
```

### For Production

When deploying to production:

1. **Set up Cognito** in AWS
2. **Set environment variables**:
   ```bash
   VITE_USER_POOL_ID=us-east-1_ABC123XYZ
   VITE_USER_POOL_CLIENT_ID=1a2b3c4d5e6f7g8h9i0j
   ```
3. **Remove DEV_MODE** from backend (or set to `false`)
4. **Frontend will automatically use Cognito** when credentials are provided

## Code Changes

### Before

```typescript
private async getAuthHeaders(): Promise<HeadersInit> {
  try {
    const session = await fetchAuthSession()
    const token = session.tokens?.idToken?.toString()
    // Always tried to get token, failed if Cognito not configured
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    }
  } catch (error) {
    throw new Error('Authentication required')  // ❌ Failed here
  }
}
```

### After

```typescript
private async getAuthHeaders(): Promise<HeadersInit> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }

  // Check if Cognito is configured
  if (!isCognitoConfigured()) {
    // Use DEV_MODE header
    headers['X-MTP-Dev-User'] = 'dev-user'
    return headers
  }

  // Try Cognito auth
  try {
    const session = await fetchAuthSession()
    const token = session.tokens?.idToken?.toString()
    headers['Authorization'] = `Bearer ${token}`
    return headers
  } catch (error) {
    // Fall back to DEV_MODE in development
    if (import.meta.env.DEV) {
      headers['X-MTP-Dev-User'] = 'dev-user'
      return headers
    }
    throw new Error('Authentication required')
  }
}
```

## Summary

✅ **Fixed**: Frontend now supports DEV_MODE when Cognito is not configured
✅ **Backward Compatible**: Still uses Cognito when configured
✅ **Development Friendly**: Works out of the box without Cognito setup
✅ **Production Ready**: Automatically switches to Cognito when credentials are provided

## Next Steps

1. **Rebuild frontend**: `docker-compose build frontend`
2. **Restart services**: `docker-compose up`
3. **Test**: Try creating a strategy or note
4. **Verify**: Check Network tab for `X-MTP-Dev-User` header

The authentication error should now be resolved! 🎉


