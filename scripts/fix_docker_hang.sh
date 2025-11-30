#!/bin/bash
# Fix Docker hanging on image pulls

set -e

echo "🔧 Fixing Docker image pull issues..."
echo ""

# Pull base images separately first
echo "📥 Pulling base images..."
docker pull node:18-alpine || echo "⚠️  Failed to pull node:18-alpine, will retry in build"
docker pull nginx:alpine || echo "⚠️  Failed to pull nginx:alpine, will retry in build"
docker pull public.ecr.aws/lambda/python:3.11 || echo "⚠️  Failed to pull Lambda image, will retry in build"

echo ""
echo "✅ Base images pulled (or will be pulled during build)"
echo ""
echo "Now try running docker-compose again:"
echo "  docker-compose up --build"


