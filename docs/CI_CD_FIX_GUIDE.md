# CI/CD Pipeline Fix Guide

## 🎯 Goal: Make CI/CD Pipeline Fully Functional

## Step 1: Configure Terraform Remote State (CRITICAL)

### Why This Is Needed

Terraform stores state locally by default. In CI/CD:
- Each run is a fresh environment
- Local state is lost between runs
- Terraform can't track what's already deployed
- **Result**: Will try to create duplicate resources or fail

### Option A: S3 Backend (Recommended)

**1. Create S3 Bucket for State:**

```bash
# Create bucket
aws s3 mb s3://mytraderpal-terraform-state --region us-east-1

# Enable versioning (for safety)
aws s3api put-bucket-versioning \
  --bucket mytraderpal-terraform-state \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket mytraderpal-terraform-state \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

**2. Create DynamoDB Table for State Locking:**

```bash
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

**3. Update `infra/terraform/main.tf`:**

Uncomment and configure the backend block:

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state backend (REQUIRED for CI/CD)
  backend "s3" {
    bucket         = "mytraderpal-terraform-state"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

**4. Initialize Terraform with Backend:**

```bash
cd infra/terraform
terraform init
# Terraform will ask to migrate existing state - type "yes"
```

### Option B: Terraform Cloud (Easier, Free Tier Available)

**1. Sign up at https://app.terraform.io**

**2. Create Organization and Workspace**

**3. Update `infra/terraform/main.tf`:**

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Terraform Cloud backend
  cloud {
    organization = "your-org-name"
    workspaces {
      name = "mytraderpal"
    }
  }
}
```

**4. Set AWS credentials in Terraform Cloud:**
- Go to workspace → Variables
- Add `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` as sensitive variables

**5. Initialize:**
```bash
cd infra/terraform
terraform login  # Follow prompts
terraform init
```

## Step 2: Configure GitHub Secrets

### Create AWS IAM User for GitHub Actions

**1. Create IAM User:**

```bash
aws iam create-user --user-name github-actions-deploy
```

**2. Create IAM Policy (with minimal required permissions):**

Create file `github-actions-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "lambda:*",
        "apigateway:*",
        "dynamodb:*",
        "cognito-idp:*",
        "iam:CreateRole",
        "iam:AttachRolePolicy",
        "iam:PutRolePolicy",
        "iam:GetRole",
        "iam:PassRole",
        "logs:CreateLogGroup",
        "logs:PutRetentionPolicy",
        "s3:*",
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

**3. Attach Policy:**

```bash
aws iam put-user-policy \
  --user-name github-actions-deploy \
  --policy-name GitHubActionsDeployPolicy \
  --policy-document file://github-actions-policy.json
```

**4. Create Access Keys:**

```bash
aws iam create-access-key --user-name github-actions-deploy
```

**Output will be:**
```json
{
  "AccessKey": {
    "AccessKeyId": "AKIA...",
    "SecretAccessKey": "...",
    "Status": "Active"
  }
}
```

**5. Add to GitHub Secrets:**

1. Go to: GitHub repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add:
   - Name: `AWS_ACCESS_KEY_ID`, Value: (from step 4)
   - Name: `AWS_SECRET_ACCESS_KEY`, Value: (from step 4)
   - Name: `AWS_REGION`, Value: `us-east-1` (optional, has default)
   - Name: `DEV_MODE`, Value: `false` (optional, has default)

## Step 3: Verify Everything Works

### Test Locally First

```bash
# 1. Test Terraform with remote state
cd infra/terraform
terraform init  # Should connect to S3/Terraform Cloud
terraform plan  # Should work

# 2. Test Docker build
docker build -f infra/docker/Dockerfile.prod -t test-image .

# 3. Verify all files exist
test -f requirements-dev.txt && echo "✅"
test -f infra/docker/Dockerfile.prod && echo "✅"
test -f src/app/.env.example && echo "✅"
test -f src/frontend-react/.env.example && echo "✅"
```

### Test in CI/CD

1. **Push to feature branch first:**
   ```bash
   git checkout -b test-ci-cd
   git push origin test-ci-cd
   ```

2. **Check GitHub Actions:**
   - Go to: GitHub → Actions tab
   - Verify `test-backend` and `test-frontend` jobs pass
   - Verify `build-docker` job passes

3. **Test deployment (on main branch):**
   ```bash
   git checkout main
   git merge test-ci-cd
   git push origin main
   ```
   - Verify `deploy` job runs
   - Check AWS Console for resources

## ✅ Checklist

Before pushing to main, verify:

- [ ] S3 bucket created for Terraform state
- [ ] DynamoDB table created for state locking
- [ ] Terraform backend configured in `main.tf`
- [ ] Terraform initialized with backend (`terraform init`)
- [ ] AWS IAM user created for GitHub Actions
- [ ] IAM user has required permissions
- [ ] Access keys created
- [ ] GitHub Secrets configured:
  - [ ] `AWS_ACCESS_KEY_ID`
  - [ ] `AWS_SECRET_ACCESS_KEY`
  - [ ] `AWS_REGION` (optional)
  - [ ] `DEV_MODE` (optional)
- [ ] All required files exist
- [ ] Tests pass locally
- [ ] Docker images build locally

## 🚨 Common Issues

### Issue: "Error: Backend configuration changed"

**Cause**: Terraform state backend not initialized

**Fix**: Run `terraform init` in `infra/terraform/`

### Issue: "Error: Missing required input 'aws-access-key-id'"

**Cause**: GitHub Secrets not configured

**Fix**: Add `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` to GitHub Secrets

### Issue: "Error: Access Denied" when pushing to ECR

**Cause**: IAM user doesn't have ECR permissions

**Fix**: Add ECR permissions to IAM policy

### Issue: "Error: S3 bucket does not exist"

**Cause**: S3 bucket for Terraform state not created

**Fix**: Create S3 bucket (see Step 1)

## 📊 Expected Pipeline Flow

```
Push to main
    ↓
✅ test-backend (2-3 min)
✅ test-frontend (1-2 min)
    ↓
✅ build-docker (3-5 min)
    ↓
✅ deploy (5-10 min)
    ├─→ Configure AWS
    ├─→ Setup Terraform
    ├─→ Create ECR repo
    ├─→ Build & push Docker image
    └─→ Deploy with Terraform
    ↓
✅ Deployment complete!
```

## 🎯 Summary

**To make CI/CD functional:**

1. ✅ **Configure Terraform remote state** (S3 or Terraform Cloud)
2. ✅ **Configure GitHub Secrets** (AWS credentials)
3. ✅ **Test on feature branch first**
4. ✅ **Then push to main**

**After these fixes:**
- ✅ All jobs will run successfully
- ✅ Tests will validate code
- ✅ Docker images will build
- ✅ Infrastructure will deploy to AWS

---

**Status**: ⚠️ **Needs configuration** - Follow this guide to make it functional

