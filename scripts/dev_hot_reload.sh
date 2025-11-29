#!/bin/bash
# Start development environment with hot reloading

set -e

echo "🚀 Starting development environment with hot reloading..."
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is required"
    exit 1
fi

# Use docker compose (newer) or docker-compose (older)
if command -v docker &> /dev/null && docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo "📦 Building and starting services..."
echo ""

$COMPOSE_CMD up --build

echo ""
echo "✅ Development environment started!"
echo ""
echo "📍 Access points:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:9000"
echo ""
echo "💡 Hot reloading is enabled:"
echo "   - Edit frontend files → Browser auto-refreshes"
echo "   - Edit backend files → Changes apply on next API request"
echo ""
echo "🛑 To stop: Ctrl+C or 'docker-compose down'"

