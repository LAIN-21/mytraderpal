#!/bin/bash
# Deploy application to AWS

set -e

echo "Deploying infrastructure..."
cd infra/cdk
npm ci
npm run build
cdk deploy --require-approval never

echo "✓ Deployment complete"


