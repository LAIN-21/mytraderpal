#!/bin/bash
# Verify that the setup is correct and services are running

set -e

echo "🔍 Verifying MyTraderPal setup..."
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is installed and running"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

echo "✅ Docker Compose is available"

# Check .env file
if [ ! -f "src/frontend-react/.env" ]; then
    echo "⚠️  Warning: src/frontend-react/.env not found"
    echo "   Run 'make install' to create it from template"
    exit 1
fi

echo "✅ Environment file exists"

# Check if containers are running
COMPOSE_CMD="docker-compose"
if ! command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker compose"
fi

if $COMPOSE_CMD ps 2>/dev/null | grep -q "Up"; then
    echo "✅ Containers are running"
    
    # Test backend health
    echo ""
    echo "Testing backend health endpoint..."
    if curl -s http://localhost:9000/v1/health >/dev/null 2>&1; then
        echo "✅ Backend is healthy"
    else
        echo "⚠️  Backend health check failed (may still be starting)"
    fi
    
    # Test frontend
    echo "Testing frontend..."
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo "✅ Frontend is accessible"
    else
        echo "⚠️  Frontend check failed (may still be starting)"
    fi
else
    echo "⚠️  Containers are not running"
    echo "   Run 'make start' to start them"
fi

echo ""
echo "✅ Setup verification complete!"

