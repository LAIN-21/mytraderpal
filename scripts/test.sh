#!/bin/bash
# Run tests with coverage

set -e

echo "Running backend tests..."
python -m pytest tests/unit/ \
  --cov=src/app \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-fail-under=70 \
  -v

echo "✓ Tests passed with 70%+ coverage"


