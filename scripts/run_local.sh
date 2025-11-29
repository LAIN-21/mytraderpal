#!/bin/bash
# Run full stack application locally with Docker Compose

set -e

echo "🚀 Starting MyTraderPal full stack..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "   Please start Docker Desktop and try again"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo "❌ Error: docker-compose is not installed"
    exit 1
fi

# Use docker compose (newer) or docker-compose (older)
if docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo "📦 Building and starting services..."
echo ""

# Build and start services
$COMPOSE_CMD up --build -d

echo ""
echo "✅ Services started successfully!"
echo ""
echo "📍 Access your application:"
echo "   Backend API:  http://localhost:9000"
echo "   Frontend App: http://localhost:3000"
echo ""
echo "📊 Health Check: http://localhost:9000/v1/health"
echo "📈 Metrics:      http://localhost:9000/v1/metrics"
echo ""
echo "💡 Useful commands:"
echo "   View logs:    $COMPOSE_CMD logs -f"
echo "   Stop:         $COMPOSE_CMD down"
echo "   Restart:      $COMPOSE_CMD restart"
echo ""

