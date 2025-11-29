#!/bin/bash
# Run frontend in development mode

set -e

echo "Starting frontend development server..."

cd src/frontend-react

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Check for .env
if [ ! -f ".env" ]; then
    echo "Warning: .env not found"
    echo "Copying from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your configuration"
fi

echo "Starting Vite dev server..."
npm run dev

