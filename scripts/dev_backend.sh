#!/bin/bash
# Run backend locally using Lambda Runtime Interface Emulator

set -e

echo "Starting backend in development mode..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is required for local Lambda development"
    echo "Install Docker or use test scripts instead"
    exit 1
fi

# Set environment variables
export TABLE_NAME=${TABLE_NAME:-mtp_app}
export DEV_MODE=${DEV_MODE:-true}
export AWS_REGION=${AWS_REGION:-us-east-1}

echo "Environment:"
echo "  TABLE_NAME=$TABLE_NAME"
echo "  DEV_MODE=$DEV_MODE"
echo "  AWS_REGION=$AWS_REGION"
echo ""

# Run Lambda locally using Docker
docker run -p 9000:8080 \
  -v "$(pwd)/src/app:/var/task" \
  -e TABLE_NAME="$TABLE_NAME" \
  -e DEV_MODE="$DEV_MODE" \
  -e AWS_REGION="$AWS_REGION" \
  public.ecr.aws/lambda/python:3.11 \
  main.handler

echo ""
echo "Backend running at http://localhost:9000"
echo "Use X-MTP-Dev-User header for authentication in dev mode"

