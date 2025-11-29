#!/bin/bash
# Pull Docker images separately before building to avoid timeouts

set -e

echo "📥 Pulling Docker base images..."
echo "This may take a few minutes, but will prevent build timeouts"
echo ""

# Pull images with retries
pull_with_retry() {
    local image=$1
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "Attempt $attempt/$max_attempts: Pulling $image..."
        if docker pull "$image"; then
            echo "✅ Successfully pulled $image"
            return 0
        else
            echo "❌ Failed to pull $image (attempt $attempt/$max_attempts)"
            if [ $attempt -lt $max_attempts ]; then
                echo "Waiting 5 seconds before retry..."
                sleep 5
            fi
            attempt=$((attempt + 1))
        fi
    done
    
    echo "⚠️  Failed to pull $image after $max_attempts attempts"
    return 1
}

# Backend image
echo "🐍 Pulling backend base image..."
pull_with_retry "public.ecr.aws/lambda/python:3.11" || echo "⚠️  Backend image pull failed, will try during build"

echo ""

# Frontend images
echo "⚛️  Pulling frontend base images..."
pull_with_retry "node:18-slim" || echo "⚠️  Node image pull failed, will try during build"
pull_with_retry "nginx:latest" || echo "⚠️  Nginx image pull failed, will try during build"

echo ""
echo "✅ Image pull complete!"
echo ""
echo "Now you can run:"
echo "  docker-compose up --build"
echo ""
echo "Or if images still fail to pull, try:"
echo "  1. Check your internet connection"
echo "  2. Restart Docker Desktop"
echo "  3. Check if you're behind a firewall/VPN"
echo "  4. Try using a different network"

