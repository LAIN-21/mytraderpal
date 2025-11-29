#!/bin/bash
# Run application without Docker (for when Docker network issues occur)

set -e

echo "🚀 Starting MyTraderPal without Docker..."
echo ""

# Check if backend script exists
if [ ! -f "scripts/dev_backend.sh" ]; then
    echo "❌ Backend script not found"
    exit 1
fi

# Start backend in background
echo "📦 Starting backend..."
./scripts/dev_backend.sh &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend
echo "⚛️  Starting frontend..."
cd src/frontend-react

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📥 Installing frontend dependencies..."
    npm install
fi

# Check for .env
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found, copying from example..."
    cp .env.example .env 2>/dev/null || true
    echo "   Please edit .env with your configuration"
fi

echo ""
echo "✅ Services starting..."
echo ""
echo "📍 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:9000"
echo ""
echo "💡 Press Ctrl+C to stop all services"
echo ""

# Start frontend (this will block)
npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID 2>/dev/null" EXIT

