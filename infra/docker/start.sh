#!/bin/bash
# Start Lambda RIE and HTTP proxy together

set -e

echo "Starting Lambda Runtime Interface Emulator and HTTP Proxy..."

# Start Lambda RIE in background on port 8080
# Use the Lambda entrypoint script to start RIE properly
# The entrypoint expects handler as first arg: app.main.handler
/usr/local/bin/aws-lambda-rie /var/runtime/bootstrap app.main.handler &
RIE_PID=$!

# Wait for RIE to be ready (check if port 8080 is listening)
echo "Waiting for Lambda RIE to start..."
for i in {1..30}; do
    if nc -z localhost 8080 2>/dev/null || curl -s http://localhost:8080/2015-03-31/functions/function/invocations >/dev/null 2>&1; then
        echo "Lambda RIE is ready!"
        break
    fi
    sleep 1
done

# Start HTTP proxy on port 9000 (foreground, so container stays alive)
echo "Starting HTTP proxy on port 9000..."
echo "Proxy will convert HTTP requests to Lambda invoke format"
exec python3 /usr/local/bin/lambda-proxy.py

