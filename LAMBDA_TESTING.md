# Testing Lambda Functions Independently

## The Issue

Lambda Runtime Interface Emulator (RIE) **does NOT convert regular HTTP requests** to Lambda events. It only accepts the **Lambda Invoke API format**.

When you do:
```bash
curl http://localhost:9000/v1/health
```

You get `404 page not found` because RIE doesn't understand this format.

## ✅ Correct Way to Test Lambda Functions

### Method 1: Use Lambda Invoke API Format

```bash
curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d '{
    "httpMethod": "GET",
    "path": "/v1/health",
    "headers": {},
    "queryStringParameters": null
  }'
```

**Response:**
```json
{
  "statusCode": 200,
  "headers": {...},
  "body": "{\"status\": \"healthy\", ...}"
}
```

### Method 2: Use Test Script

```bash
./scripts/test_lambda.sh
```

This script tests multiple endpoints using the correct format.

### Method 3: Test Handler Directly in Container

```bash
docker-compose exec api python3 -c "
from app.main import handler
import json

event = {
    'httpMethod': 'GET',
    'path': '/v1/health',
    'headers': {},
    'queryStringParameters': None
}

result = handler(event, None)
print(json.dumps(json.loads(result['body']), indent=2))
"
```

## Why This Happens

Lambda RIE is designed to emulate the **Lambda service**, not API Gateway. It expects:
- Lambda invoke API format: `POST /2015-03-31/functions/function/invocations`
- Event payload as JSON in the request body

It does **NOT**:
- Convert HTTP requests automatically
- Act as a web server
- Handle routes like `/v1/health` directly

## Solutions for HTTP-like Access

### Option 1: Use Lambda Invoke Format (Current)
✅ Works now  
✅ Matches AWS Lambda behavior  
❌ Not HTTP-like

### Option 2: Add HTTP Proxy (Future Enhancement)
We could add a simple HTTP proxy that converts HTTP requests to Lambda events:

```python
# Simple Flask/FastAPI proxy
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    event = convert_http_to_lambda_event(request)
    result = handler(event, None)
    return convert_lambda_response_to_http(result)
```

### Option 3: Use SAM Local or Serverless Offline
These tools provide HTTP-like access:
- AWS SAM Local
- Serverless Framework with serverless-offline plugin

## Current Status

✅ **Lambda handler works perfectly** - tested directly  
✅ **Lambda RIE works** - accepts invoke format  
❌ **Direct HTTP access** - not supported by RIE  

## Testing Checklist

- [x] Lambda handler imports correctly
- [x] Lambda handler executes successfully
- [x] Lambda handler returns correct responses
- [x] Lambda RIE accepts invoke format
- [ ] Direct HTTP access (requires proxy or different tool)

## Quick Test Commands

```bash
# Test health endpoint
curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d '{"httpMethod":"GET","path":"/v1/health","headers":{},"queryStringParameters":null}'

# Test with dev user
curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d '{
    "httpMethod": "POST",
    "path": "/v1/notes",
    "headers": {"X-MTP-Dev-User": "test-user"},
    "body": "{\"date\":\"2025-11-30\",\"text\":\"Test\"}",
    "queryStringParameters": null
  }'

# Use test script
./scripts/test_lambda.sh
```

## For Frontend Development

The frontend needs to call the backend. Since RIE doesn't support direct HTTP, you have two options:

1. **Deploy to AWS** - API Gateway handles HTTP → Lambda conversion
2. **Add HTTP proxy** - Convert HTTP requests to Lambda invoke format
3. **Use test script** - Test backend independently, develop frontend separately

## Summary

Your Lambda function **is functional** ✅. The "404" error is just because Lambda RIE doesn't support direct HTTP requests - it only accepts the Lambda invoke API format. This is expected behavior.

