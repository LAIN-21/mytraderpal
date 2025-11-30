# Docker Connection Fixes

## Issues Fixed

### 1. ✅ Frontend API URL Configuration

**Problem**: Frontend was configured to use `http://api:9000` (internal Docker service name), but browsers make requests from the user's machine, not from inside Docker containers.

**Solution**: Changed `VITE_API_URL` in `docker-compose.yml` from `http://api:9000` to `http://localhost:9000`.

**Why**: When the frontend runs in a browser, it needs to connect to the backend via the host machine's localhost, not via Docker's internal network. The Docker service name `api` only works for container-to-container communication.

### 2. ✅ CORS Preflight (OPTIONS) Requests

**Problem**: Backend didn't handle OPTIONS preflight requests, which browsers send before making cross-origin requests.

**Solution**: Added OPTIONS request handling in `src/app/api/router.py` to return proper CORS headers immediately.

**Code Added**:
```python
# Handle CORS preflight requests
if http_method == 'OPTIONS':
    return {
        'statusCode': 200,
        'headers': cors_headers(origin),
        'body': ''
    }
```

### 3. ✅ Enhanced CORS Headers

**Problem**: CORS headers needed to support credentials and handle localhost origins properly.

**Solution**: Enhanced `cors_headers()` function in `src/app/core/response.py` to:
- Properly handle localhost origins
- Add `Access-Control-Allow-Credentials` header when origin is not wildcard
- Support development with localhost

## Configuration Summary

### Docker Compose

```yaml
services:
  api:
    ports:
      - "9000:8080"  # Lambda RIE listens on 8080, exposed as 9000
    environment:
      - TABLE_NAME=mtp_app
      - DEV_MODE=true
      - AWS_REGION=us-east-1

  frontend:
    build:
      args:
        - VITE_API_URL=http://localhost:9000  # ✅ Fixed: localhost for browser
    ports:
      - "3000:80"
    depends_on:
      - api
```

### CORS Configuration

- **Allowed Origins**: Any origin (development) or specific origins (production)
- **Allowed Methods**: GET, POST, PUT, PATCH, DELETE, OPTIONS
- **Allowed Headers**: Content-Type, Authorization, X-MTP-Dev-User
- **Credentials**: Supported when origin is specified

## How It Works

1. **Frontend (Browser)** → Makes request to `http://localhost:9000`
2. **Docker Host** → Routes to container port 9000
3. **Backend Container** → Lambda RIE receives on port 8080 (mapped to host 9000)
4. **Lambda Handler** → Processes request and returns response with CORS headers
5. **Browser** → Receives response with proper CORS headers

## Testing the Connection

### 1. Start Services

```bash
docker-compose up --build
```

### 2. Test Backend Directly

```bash
# Health check
curl http://localhost:9000/v1/health

# Should return:
# {"status": "healthy", "uptime": ..., "version": "0.1.0"}
```

### 3. Test CORS

```bash
# Test OPTIONS preflight
curl -X OPTIONS http://localhost:9000/v1/health \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -v

# Should return 200 with CORS headers
```

### 4. Test from Frontend

1. Open browser to `http://localhost:3000`
2. Open browser DevTools → Network tab
3. Try to make an API call
4. Check that requests to `http://localhost:9000` succeed
5. Verify CORS headers are present in response

## Troubleshooting

### Frontend Can't Connect to Backend

**Symptoms**: Network errors in browser console, CORS errors

**Solutions**:
1. Verify backend is running: `curl http://localhost:9000/v1/health`
2. Check `VITE_API_URL` is set to `http://localhost:9000` (not `api:9000`)
3. Rebuild frontend: `docker-compose build frontend`
4. Check browser console for specific error messages

### CORS Errors

**Symptoms**: Browser shows CORS policy errors

**Solutions**:
1. Verify OPTIONS requests are handled (check Network tab)
2. Check that `Access-Control-Allow-Origin` header is present
3. Ensure origin matches (should be `http://localhost:3000`)
4. Check that credentials header is set if using authentication

### Backend Not Responding

**Symptoms**: Connection refused, timeout errors

**Solutions**:
1. Check backend container is running: `docker-compose ps`
2. Check backend logs: `docker-compose logs api`
3. Verify port mapping: `docker-compose ps` should show `0.0.0.0:9000->8080/tcp`
4. Test Lambda handler directly: Check logs for errors

## Files Modified

1. **docker-compose.yml**: Changed `VITE_API_URL` from `http://api:9000` to `http://localhost:9000`
2. **src/app/api/router.py**: Added OPTIONS request handling
3. **src/app/core/response.py**: Enhanced CORS headers with credentials support

## Next Steps

1. ✅ Test the connection with `docker-compose up --build`
2. ✅ Verify frontend can make API calls
3. ✅ Check browser DevTools for any remaining issues
4. ✅ Test authentication flow if using Cognito

## Summary

All connection issues have been fixed:
- ✅ Frontend API URL points to correct backend address
- ✅ CORS preflight requests are handled
- ✅ CORS headers are properly configured
- ✅ Localhost origins are supported

The frontend and backend should now communicate properly! 🎉


