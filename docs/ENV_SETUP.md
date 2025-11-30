# Environment Variables Setup Guide

## Frontend (.env file)

**Location:** `src/frontend-react/.env`

**Format:**
```env
# API Configuration
VITE_API_URL=http://localhost:9000

# AWS Cognito Configuration
VITE_USER_POOL_ID=your-user-pool-id-here
VITE_USER_POOL_CLIENT_ID=your-client-id-here
VITE_AWS_REGION=us-east-1
```

**How to create:**
```bash
cd src/frontend-react
cp .env.example .env
# Then edit .env with your actual values
```

**Important Notes:**
- All frontend environment variables **must** start with `VITE_` prefix (this is required by Vite)
- These variables are embedded at build time, so you need to rebuild if you change them
- For development, you can use the `.env` file
- For production builds, set these as build arguments in Docker or CI/CD

## Backend Environment Variables

The backend (Lambda function) doesn't use a `.env` file. Instead, environment variables are set:

### For Local Development (Docker):
Set in `docker-compose.yml` or pass as environment variables:
```bash
TABLE_NAME=mtp_app
DEV_MODE=true
AWS_REGION=us-east-1
```

### For Local Testing (Scripts):
Set as environment variables before running:
```bash
export TABLE_NAME=mtp_app
export DEV_MODE=true
export AWS_REGION=us-east-1
./scripts/dev_backend.sh
```

### For AWS Lambda (Production):
Set via AWS Console, CDK, or AWS CLI:
```bash
aws lambda update-function-configuration \
  --function-name MyTraderPalStack-ApiFunction-xxxxx \
  --environment Variables='{TABLE_NAME=mtp_app,DEV_MODE=false,AWS_REGION=us-east-1}'
```

## Quick Setup Steps

### 1. Frontend Setup
```bash
# Navigate to frontend directory
cd src/frontend-react

# Copy example file
cp .env.example .env

# Edit .env with your values
# You'll need:
# - VITE_API_URL: Your API Gateway URL (or http://localhost:9000 for local)
# - VITE_USER_POOL_ID: From AWS Cognito User Pool
# - VITE_USER_POOL_CLIENT_ID: From AWS Cognito User Pool
# - VITE_AWS_REGION: AWS region (e.g., us-east-1)
```

### 2. Get Your AWS Cognito Values

1. Go to AWS Console → Cognito → User Pools
2. Select your user pool
3. Copy the **User Pool ID** → use for `VITE_USER_POOL_ID`
4. Go to **App integration** → **App clients**
5. Copy the **Client ID** → use for `VITE_USER_POOL_CLIENT_ID`

### 3. Get Your API URL

- **Local development:** `http://localhost:9000`
- **Deployed API:** Get from CDK stack outputs:
  ```bash
  cd infra/cdk
  cdk deploy
  # Look for "ApiUrl" in the output
  ```

## Example .env File (Frontend)

```env
# For local development pointing to local backend
VITE_API_URL=http://localhost:9000
VITE_USER_POOL_ID=us-east-1_ABC123XYZ
VITE_USER_POOL_CLIENT_ID=1a2b3c4d5e6f7g8h9i0j
VITE_AWS_REGION=us-east-1
```

```env
# For production pointing to deployed API
VITE_API_URL=https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
VITE_USER_POOL_ID=us-east-1_ABC123XYZ
VITE_USER_POOL_CLIENT_ID=1a2b3c4d5e6f7g8h9i0j
VITE_AWS_REGION=us-east-1
```

## Troubleshooting

### Frontend can't connect to API
- Check `VITE_API_URL` is correct
- Make sure backend is running (if using local)
- Check CORS settings in backend

### Authentication not working
- Verify `VITE_USER_POOL_ID` and `VITE_USER_POOL_CLIENT_ID` are correct
- Check that `VITE_AWS_REGION` matches your Cognito region
- Make sure you've rebuilt the frontend after changing `.env` (Vite requires rebuild for env changes)

### Environment variables not working
- **Frontend:** Must start with `VITE_` prefix
- **Frontend:** Need to restart dev server or rebuild after changes
- **Backend:** Set via Docker environment or AWS Lambda configuration

## Security Notes

⚠️ **Never commit `.env` files to git!**
- `.env` is already in `.gitignore`
- Only commit `.env.example` files
- Use GitHub Secrets for CI/CD pipelines


