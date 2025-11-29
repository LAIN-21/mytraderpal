#!/bin/bash
# Run linters

set -e

echo "Running Python linter..."
flake8 src/app --max-line-length=120 --exclude=__pycache__,*.pyc

echo "Running frontend linter..."
cd src/frontend
npm run lint || true

echo "✓ Linting complete"

