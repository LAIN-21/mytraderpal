# Deployment Checklist - Pre-Push Validation

This checklist ensures everything is configured correctly before pushing to main.

## ✅ File Existence Check

### Required Files

- [x] `src/app/.env.example` - Backend environment template
- [x] `src/frontend-react/.env.example` - Frontend environment template
- [x] `infra/docker/Dockerfile.prod` - Production Dockerfile
- [x] `infra/terraform/terraform.tfvars.example` - Terraform configuration template
- [x] `requirements-dev.txt` - Development dependencies
- [x] `.github/workflows/ci.yml` - CI/CD pipeline

## 🔐 GitHub Secrets Required

These secrets must be configured in GitHub repository settings:

### Required (Deployment will fail without these):

1. **AWS_ACCESS_KEY_ID** ⚠️ **REQUIRED**
   - Used for: AWS authentication in CI/CD
   - Where: `.github/workflows/ci.yml` line 137
   - **Action**: Must be set in GitHub Secrets

2. **AWS_SECRET_ACCESS_KEY** ⚠️ **REQUIRED**
   - Used for: AWS authentication in CI/CD
   - Where: `.github/workflows/ci.yml` line 138
   - **Action**: Must be set in GitHub Secrets

### Optional (Have defaults, but should be set for production):

3. **AWS_REGION**
   - Default: `us-east-1`
   - Used for: AWS region configuration
   - **Action**: Set if using different region

4. **DEV_MODE**
   - Default: `false` (in CI/CD)
   - Used for: Lambda environment variable
   - **Action**: Set to `false` for production

5. **VITE_API_URL**
   - Default: `http://localhost:9000` (for tests)
   - Used for: Frontend build
   - **Action**: Not needed (frontend built separately)

6. **VITE_USER_POOL_ID**
   - Default: `test` (for tests)
   - Used for: Frontend build
   - **Action**: Not needed (frontend built separately)

7. **VITE_USER_POOL_CLIENT_ID**
   - Default: `test` (for tests)
   - Used for: Frontend build
   - **Action**: Not needed (frontend built separately)

8. **VITE_AWS_REGION**
   - Default: `us-east-1`
   - Used for: Frontend build
   - **Action**: Not needed (frontend built separately)

## 📝 Environment Files

### Development (Local)

**Backend** (`src/app/.env`):
```env
TABLE_NAME=mtp_app
DEV_MODE=true
AWS_REGION=us-east-1
```
✅ Created automatically by `make install`
✅ Has `.env.example` template

**Frontend** (`src/frontend-react/.env`):
```env
VITE_API_URL=http://localhost:9000
VITE_USER_POOL_ID=
VITE_USER_POOL_CLIENT_ID=
VITE_AWS_REGION=us-east-1
```
✅ Created automatically by `make install`
✅ Has `.env.example` template

### Production (AWS)

**Backend Environment Variables:**
- ✅ Set by Terraform in `infra/terraform/main.tf`
- ✅ No `.env` file needed in production
- ✅ Variables: `TABLE_NAME`, `DEV_MODE`, `AWS_REGION`

**Frontend Environment Variables:**
- ✅ Set at build time in CI/CD
- ✅ Or set in hosting platform (Amplify, etc.)

## 🚀 CI/CD Pipeline Validation

### What Runs on Push to Main

1. **Test Backend** ✅
   - Runs: `pytest tests/ --cov=src/app --cov-fail-under=70`
   - Requires: `requirements.txt`, `requirements-dev.txt`
   - ✅ Should pass if tests are written

2. **Test Frontend** ✅
   - Runs: `npm ci`, `npm run lint`, `npm run build`
   - Requires: `src/frontend-react/package.json`
   - ✅ Should pass if no build errors

3. **Build Docker Images** ✅
   - Builds: Backend and frontend Docker images
   - Requires: `infra/docker/Dockerfile`, `src/frontend-react/infra/docker/Dockerfile`
   - ✅ Should pass if Dockerfiles are correct

4. **Deploy** ⚠️ **REQUIRES SECRETS**
   - Requires: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
   - Builds: Production Docker image (`Dockerfile.prod`)
   - Pushes: To ECR
   - Deploys: With Terraform
   - ✅ Will fail if secrets are missing

## ⚠️ Potential Issues

### 1. Missing GitHub Secrets

**Symptom**: Deployment job fails with "AWS credentials not configured"

**Fix**:
1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Add:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION` (optional, defaults to us-east-1)
   - `DEV_MODE` (optional, defaults to false)

### 2. Terraform Configuration Issues

**Check**: `infra/terraform/terraform.tfvars.example` has correct values:
- ✅ `lambda_handler = "app.main.handler"` (not `main.handler`)
- ✅ `lambda_timeout = 30`
- ✅ `cognito_domain_prefix` is unique

### 3. Dockerfile Issues

**Check**: `infra/docker/Dockerfile.prod` exists and is correct:
- ✅ Uses `FROM public.ecr.aws/lambda/python:3.11`
- ✅ Copies `requirements.txt`
- ✅ Copies `src/app` to `${LAMBDA_TASK_ROOT}/app`
- ✅ CMD is `["app.main.handler"]`

### 4. Missing Dependencies

**Check**: All required files exist:
- ✅ `requirements.txt` (backend dependencies)
- ✅ `requirements-dev.txt` (test dependencies)
- ✅ `src/frontend-react/package.json` (frontend dependencies)

## ✅ Pre-Push Checklist

Before pushing to main, verify:

- [ ] All tests pass locally: `pytest tests/`
- [ ] Frontend builds: `cd src/frontend-react && npm run build`
- [ ] Docker images build: `docker build -f infra/docker/Dockerfile.prod .`
- [ ] GitHub Secrets are configured:
  - [ ] `AWS_ACCESS_KEY_ID`
  - [ ] `AWS_SECRET_ACCESS_KEY`
  - [ ] `AWS_REGION` (optional)
  - [ ] `DEV_MODE` (optional)
- [ ] `.env.example` files exist and are correct
- [ ] `terraform.tfvars.example` has correct handler: `app.main.handler`
- [ ] `Dockerfile.prod` exists and is correct
- [ ] No hardcoded credentials in code
- [ ] All environment variables have defaults or are documented

## 🔍 Quick Validation Commands

```bash
# Check all required files exist
test -f src/app/.env.example && echo "✅ Backend .env.example" || echo "❌ Missing"
test -f src/frontend-react/.env.example && echo "✅ Frontend .env.example" || echo "❌ Missing"
test -f infra/docker/Dockerfile.prod && echo "✅ Dockerfile.prod" || echo "❌ Missing"
test -f requirements-dev.txt && echo "✅ requirements-dev.txt" || echo "❌ Missing"

# Check Terraform config
grep -q 'lambda_handler = "app.main.handler"' infra/terraform/terraform.tfvars.example && echo "✅ Handler correct" || echo "❌ Handler incorrect"

# Check CI/CD references
grep -q 'AWS_ACCESS_KEY_ID' .github/workflows/ci.yml && echo "✅ CI/CD has AWS secrets" || echo "❌ Missing"
```

## 📋 Summary

### ✅ What's Already Good

- ✅ All `.env.example` files exist
- ✅ `Dockerfile.prod` exists
- ✅ CI/CD pipeline is configured
- ✅ Terraform configuration exists
- ✅ All required files are in place

### ⚠️ What Needs Action

- ⚠️ **GitHub Secrets must be configured** before first deployment:
  - `AWS_ACCESS_KEY_ID` (REQUIRED)
  - `AWS_SECRET_ACCESS_KEY` (REQUIRED)
  - `AWS_REGION` (optional, defaults to us-east-1)
  - `DEV_MODE` (optional, defaults to false)

### 🎯 Next Steps

1. **Configure GitHub Secrets** (if not done):
   ```bash
   # Go to: GitHub → Settings → Secrets and variables → Actions
   # Add: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
   ```

2. **Test Locally**:
   ```bash
   make install
   make start
   make verify
   ```

3. **Push to Main**:
   ```bash
   git push origin main
   # CI/CD will run automatically
   ```

4. **Monitor Deployment**:
   - Check GitHub Actions tab
   - Verify all jobs pass
   - Check AWS Console for resources

## 🆘 If Deployment Fails

1. **Check GitHub Actions logs** for specific error
2. **Verify secrets are set** in repository settings
3. **Check AWS credentials** have correct permissions:
   - ECR: Push/pull images
   - Lambda: Create/update functions
   - API Gateway: Create/update APIs
   - DynamoDB: Create tables
   - Cognito: Create user pools
   - IAM: Create roles and policies
4. **Verify Terraform state** (if using remote state)

---

**Last Updated**: After migration to Docker container images
**Status**: ✅ Ready for deployment (requires GitHub Secrets configuration)

