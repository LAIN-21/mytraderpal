#!/bin/bash
# Test Lambda function directly using Lambda invoke API format

set -e

API_URL="${1:-http://localhost:9000}"

echo "🧪 Testing Lambda Function Directly"
echo "===================================="
echo ""

# Test health endpoint
echo "1. Testing /v1/health endpoint..."
HEALTH_RESPONSE=$(curl -s -X POST "${API_URL}/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d '{
    "httpMethod": "GET",
    "path": "/v1/health",
    "headers": {},
    "queryStringParameters": null
  }')

echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
echo ""

# Test metrics endpoint
echo "2. Testing /v1/metrics endpoint..."
METRICS_RESPONSE=$(curl -s -X POST "${API_URL}/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d '{
    "httpMethod": "GET",
    "path": "/v1/metrics",
    "headers": {},
    "queryStringParameters": null
  }')

echo "$METRICS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$METRICS_RESPONSE"
echo ""

# Test creating a note (with dev user)
echo "3. Testing POST /v1/notes (with dev user)..."
NOTE_RESPONSE=$(curl -s -X POST "${API_URL}/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d '{
    "httpMethod": "POST",
    "path": "/v1/notes",
    "headers": {
      "X-MTP-Dev-User": "test-user-123",
      "Content-Type": "application/json"
    },
    "body": "{\"date\":\"2025-11-30\",\"text\":\"Test note from Lambda test\"}",
    "queryStringParameters": null
  }')

echo "$NOTE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$NOTE_RESPONSE"
echo ""

echo "✅ Lambda function tests complete!"
echo ""
echo "Note: Lambda RIE only accepts the Lambda invoke API format."
echo "For HTTP-like requests, use the format shown above."

