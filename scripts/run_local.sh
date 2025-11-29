#!/bin/bash
# Run application locally

set -e

echo "Starting local development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running"
    exit 1
fi

# Start services with docker-compose
cd infra/docker
docker-compose up -d

echo "✓ Local environment started"
echo "Backend: http://localhost:9000"
echo "Frontend: http://localhost:3000"

