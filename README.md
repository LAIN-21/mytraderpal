# MyTraderPal

A trading journal application for tracking trades, strategies, and market observations.

## Quick Start

```bash
git clone <repository-url>
cd mytraderpal
make install
make start
```

Application runs at:
- Frontend: http://localhost:3000
- Backend: http://localhost:9000

**Prerequisites:** Docker Desktop installed and running

## Commands

```bash
make test      # Run tests
make logs      # View logs
make stop      # Stop containers
```

## Production Deployment

**Required GitHub Secrets:**
- `AWS_ACCESS_KEY_ID` (required)
- `AWS_SECRET_ACCESS_KEY` (required)

**CI/CD:** Push to `main` branch - deployment is automatic.

## How It Works

**When you clone and run `make install` + `make start`:**

1. **Backend** (`src/app/.env`):
   - `DEV_MODE=true` (default)
   - Backend accepts `X-MTP-Dev-User` header for authentication
   - All requests authenticated as "dev-user" (no Cognito needed)

2. **Frontend** (`src/frontend-react/.env`):
   - Cognito values empty (default)
   - Frontend detects no Cognito config
   - Automatically sends `X-MTP-Dev-User: dev-user` header
   - All data saved to "dev-user" account

**This is expected behavior for local development!**

**If you set `DEV_MODE=false` in `src/app/.env`:**
- Backend will require real Cognito authentication
- Frontend must have `VITE_USER_POOL_ID` and `VITE_USER_POOL_CLIENT_ID` configured
- Without Cognito, you'll get 401 Unauthorized errors

## What Gets Deployed to AWS

**On commit to `main` branch:**

1. **Backend Code** (Docker image):
   - `src/app/` - All Python code (main.py, api/, core/, services/, repositories/, models/)
   - `requirements.txt` - Python dependencies
   - Built into container image → Pushed to ECR → Deployed to Lambda

2. **Frontend Code** (S3 + CloudFront):
   - `src/frontend-react/` - All React/TypeScript code
   - Built with `npm run build` → Deployed to S3 → Served via CloudFront
   - Frontend URL available in Terraform outputs

3. **Infrastructure** (Terraform):
   - Lambda function (with new container image)
   - API Gateway
   - DynamoDB table
   - Cognito (if not exists)
   - S3 bucket (frontend hosting)
   - CloudFront distribution (CDN for frontend)

## License

MIT
