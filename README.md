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

## Prerequisites

**Required:**
- **Docker Desktop** - Install and ensure it's running
  - Download: https://www.docker.com/products/docker-desktop
  - Verify: `docker --version` and `docker info`
- **Git** - For cloning the repository
- **Make** - Usually pre-installed on Mac/Linux

**Optional (for local testing):**
- **Python 3.11+** - For running tests locally
- **Node.js 18+** - For frontend development (Docker handles this automatically)

## Commands

```bash
make install   # Setup environment and install dependencies
make start     # Start all services (frontend + backend)
make stop      # Stop all containers
make restart   # Restart all containers
make test      # Run tests (uses Python virtual environment)
make logs      # View container logs
make verify    # Verify services are running correctly
```

## What `make install` Does

The `make install` command automatically:
1. ✅ Checks prerequisites (Docker, Make)
2. ✅ Creates `.env` files:
   - `src/app/.env` - Backend configuration (DEV_MODE, TABLE_NAME, AWS_REGION)
   - `src/frontend-react/.env` - Frontend configuration (API URL, Cognito settings)
3. ✅ Sets up Python virtual environment (`.venv`) and installs dependencies
4. ✅ Installs frontend npm dependencies
5. ✅ Checks for optional tools (Terraform, AWS CLI)

**Note:** All `.env` files are created automatically with default values for local development.

## Testing for Fresh Clones

To verify everything works for someone cloning the repo:

```bash
# Test in a completely fresh directory
cd /tmp  # or any directory outside your project
git clone <your-repo-url> mytraderpal-test
cd mytraderpal-test
make install
make start
```

**What should work:**
- ✅ `make install` creates all `.env` files automatically
- ✅ `make start` starts frontend and backend
- ✅ Frontend at http://localhost:3000
- ✅ Backend at http://localhost:9000
- ✅ All local development features work (DEV_MODE)

**What won't work (and that's expected):**
- ❌ **Production deployment** - Requires GitHub Secrets (see below)

## Production Deployment

### Important: GitHub Secrets Are Repository-Specific

**⚠️ When someone forks or clones your repository:**
- They do **NOT** have access to your GitHub Secrets
- Secrets are stored per-repository in GitHub Settings
- Forks/clones need to set up their own secrets for deployment

**What this means:**
- ✅ **Local development** works immediately (no secrets needed)
- ❌ **CI/CD deployment** won't work until they configure their own secrets

### Required GitHub Secrets

For automatic deployment via CI/CD, you need to configure these GitHub Secrets in **your own repository**:

1. **`AWS_ACCESS_KEY_ID`** (required)
2. **`AWS_SECRET_ACCESS_KEY`** (required)
3. **`VITE_USER_POOL_ID`** (optional, for Cognito authentication)
4. **`VITE_USER_POOL_CLIENT_ID`** (optional, for Cognito authentication)
5. **`AWS_REGION`** (optional, defaults to `us-east-1`)
6. **`DEV_MODE`** (optional, defaults to `false` for production)

### How to Get AWS Credentials

1. **Log in to AWS Console**: https://console.aws.amazon.com
2. **Go to IAM** → Users → Your User → Security Credentials
3. **Create Access Key**:
   - Click "Create access key"
   - Choose "Command Line Interface (CLI)" or "Application running outside AWS"
   - Download or copy the credentials:
     - **Access Key ID** → Use as `AWS_ACCESS_KEY_ID`
     - **Secret Access Key** → Use as `AWS_SECRET_ACCESS_KEY`
   - ⚠️ **Important**: Save these immediately - the secret key is only shown once!

### How to Get Cognito Values (After First Deployment)

After the first deployment, Cognito resources are created automatically. Get the values:

1. **Via Terraform Output** (recommended):
   ```bash
   cd infra/terraform
   terraform output user_pool_id
   terraform output user_pool_client_id
   ```

2. **Via AWS Console**:
   - Go to AWS Console → Cognito → User Pools
   - Find your user pool (named `mytraderpal-users`)
   - Copy the **User Pool ID**
   - Go to App Integration → App Clients
   - Copy the **Client ID**

3. **Add to GitHub Secrets**:
   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Add `VITE_USER_POOL_ID` and `VITE_USER_POOL_CLIENT_ID`
   - These will be used in the next frontend build

**Note**: On the first deployment, Cognito values won't exist yet. After the first successful deployment, add them to GitHub Secrets for subsequent deployments.

### CI/CD Deployment

**Automatic Deployment:** Push to `main` branch - deployment is automatic.

The CI/CD pipeline will:
1. Run tests (backend + frontend)
2. Build Docker image for backend
3. Deploy infrastructure with Terraform
4. Build and deploy frontend to S3 + CloudFront
5. Output deployment URLs in the workflow logs

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
