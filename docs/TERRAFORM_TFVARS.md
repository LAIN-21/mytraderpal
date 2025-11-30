# Terraform.tfvars - When Do You Need It?

## Quick Answer

**For CI/CD (GitHub Actions):** ❌ **No** - CI/CD creates `terraform.tfvars` automatically  
**For local Terraform runs:** ✅ **Yes** - Create `terraform.tfvars` from the example

## Detailed Explanation

### CI/CD Pipeline (Automatic)

The GitHub Actions workflow (`.github/workflows/ci.yml`) **automatically creates** `terraform.tfvars` during deployment:

```yaml
# In deploy job, step "Create ECR repository (if needed)"
cat > terraform.tfvars <<EOF
aws_region = "${{ secrets.AWS_REGION || 'us-east-1' }}"
environment = "production"
# ... etc
EOF
```

**So for CI/CD:**
- ✅ No `terraform.tfvars` file needed in repository
- ✅ CI/CD generates it from GitHub Secrets
- ✅ Each deployment gets fresh values

### Local Terraform Runs (Manual)

If you want to run Terraform **locally** (not via CI/CD), you need `terraform.tfvars`:

**When you'd run Terraform locally:**
- Testing infrastructure changes before pushing
- Manual deployments
- Troubleshooting
- Development/testing

**To create it:**

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Then edit terraform.tfvars with your values
```

## What Should Be in terraform.tfvars?

### For Local Development/Testing

```hcl
# AWS Configuration
aws_region  = "us-east-1"
environment = "dev"

# DynamoDB
table_name = "mtp_app"

# Cognito
user_pool_name        = "mytraderpal-users"
cognito_domain_prefix = "mytraderpal-dev-$(date +%s)"  # Make it unique

# Cognito OAuth URLs
cognito_callback_urls = [
  "http://localhost:3000/login"
]

cognito_logout_urls = [
  "http://localhost:3000/"
]

# Lambda
lambda_function_name = "mytraderpal-api"
lambda_handler       = "app.main.handler"
lambda_timeout       = 30

# Lambda container image (for local testing, leave empty to use latest)
lambda_image_uri = ""

# API Gateway
api_name = "mytraderpal-api"

# Development Mode
dev_mode          = "true"
enable_cognito_auth = false

# CORS Configuration
cors_allowed_origins = [
  "http://localhost:3000"
]

cors_allowed_headers = [
  "Content-Type",
  "Authorization",
  "X-MTP-Dev-User"
]

cors_allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
```

### Important Notes

1. **`terraform.tfvars` is in `.gitignore`** ✅
   - Won't be committed to repository
   - Safe to store local values

2. **`cognito_domain_prefix` must be globally unique**
   - Use timestamp or random string
   - Example: `mytraderpal-dev-$(date +%s)`

3. **`lambda_image_uri` for local testing:**
   - Leave empty to use `ECR_REPO:latest`
   - Or specify specific image: `123456789012.dkr.ecr.us-east-1.amazonaws.com/mytraderpal-api-repo:abc123`

## Recommendation

### Option 1: CI/CD Only (Recommended for Production)

**Don't create `terraform.tfvars` locally:**
- ✅ Let CI/CD handle deployments
- ✅ No local Terraform needed
- ✅ Consistent deployments

**When to use:** Production deployments via GitHub Actions

### Option 2: Local + CI/CD (For Development)

**Create `terraform.tfvars` for local testing:**
- ✅ Test infrastructure changes locally
- ✅ Faster iteration
- ✅ Debug issues before pushing

**When to use:** 
- Testing Terraform changes
- Manual deployments
- Development environment setup

## Summary

| Scenario | Need terraform.tfvars? | How to Get It |
|----------|------------------------|---------------|
| **CI/CD Deployment** | ❌ No | CI/CD creates it automatically |
| **Local Terraform Plan** | ✅ Yes | Copy from `terraform.tfvars.example` |
| **Local Terraform Apply** | ✅ Yes | Copy from `terraform.tfvars.example` |
| **Just Running Tests** | ❌ No | Not needed |

## Quick Commands

```bash
# Create terraform.tfvars for local use
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
# (Use your favorite editor)

# Then use Terraform
terraform plan
terraform apply
```

---

**Bottom Line:** 
- **For CI/CD**: No `terraform.tfvars` needed - it's created automatically
- **For local runs**: Yes, create it from the example file

