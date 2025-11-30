# Migration Guide: CDK to Terraform

This guide helps you migrate from AWS CDK to Terraform for MyTraderPal infrastructure.

## Why Terraform?

- **Better AWS connectivity**: Terraform's AWS provider is more mature and stable
- **Simpler debugging**: Clear error messages and state management
- **Industry standard**: Widely adopted across teams
- **Better state management**: Explicit state files and locking
- **Easier troubleshooting**: Direct resource visibility

## Prerequisites

1. **Terraform** >= 1.5.0
   ```bash
   brew install terraform  # macOS
   ```

2. **AWS CLI** configured
   ```bash
   aws configure
   ```

3. **Python 3.11+** (for Lambda dependencies)

## Migration Options

### Option 1: Fresh Start (Recommended)

Start with a clean slate. This is simplest if you're okay with recreating resources.

1. **Destroy CDK stack:**
   ```bash
   cd infra/cdk
   cdk destroy
   ```

2. **Deploy with Terraform:**
   ```bash
   cd ../terraform
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars
   terraform init
   terraform apply
   ```

3. **Update frontend .env** with Terraform outputs:
   ```bash
   terraform output
   ```

### Option 2: Import Existing Resources

Keep your existing resources and import them into Terraform.

1. **Get resource IDs from CDK:**
   ```bash
   cd infra/cdk
   cdk synth
   # Check cdk.out/MyTraderPalStack.template.json for resource IDs
   ```

2. **Import into Terraform:**
   ```bash
   cd ../terraform
   terraform init
   
   # Import DynamoDB table
   terraform import module.dynamodb.aws_dynamodb_table.main mtp_app
   
   # Import Cognito User Pool
   terraform import module.cognito.aws_cognito_user_pool.main <user-pool-id>
   
   # Import Cognito User Pool Client
   terraform import module.cognito.aws_cognito_user_pool_client.main <user-pool-id>/<client-id>
   
   # Import Lambda Function
   terraform import module.lambda.aws_lambda_function.main mytraderpal-api
   
   # Import API Gateway (more complex, see below)
   ```

3. **Verify import:**
   ```bash
   terraform plan
   # Should show minimal or no changes
   ```

### Option 3: Gradual Migration

Run both CDK and Terraform side-by-side, then switch over.

1. **Deploy new resources with Terraform** (different names)
2. **Update application** to use new resources
3. **Destroy old CDK stack** once verified

## Step-by-Step: Fresh Start

### 1. Backup Current Configuration

```bash
# Export CDK outputs
cd infra/cdk
cdk synth > cdk-output-backup.json

# Note down important values:
# - User Pool ID
# - User Pool Client ID
# - API Gateway URL
# - DynamoDB table name
```

### 2. Configure Terraform

```bash
cd ../terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
aws_region  = "us-east-1"
environment = "dev"

# Cognito domain must be globally unique
cognito_domain_prefix = "mytraderpal-dev-$(date +%s)"  # Use timestamp for uniqueness

# Update OAuth URLs if needed
cognito_callback_urls = [
  "http://localhost:3000/login",
  "https://your-app.amplifyapp.com/login"
]
```

### 3. Initialize and Deploy

```bash
terraform init
terraform plan  # Review changes
terraform apply
```

### 4. Update Frontend Configuration

After deployment, get outputs:

```bash
terraform output
```

Update `src/frontend-react/.env`:

```env
VITE_API_URL=https://<api-id>.execute-api.us-east-1.amazonaws.com/prod
VITE_USER_POOL_ID=<user-pool-id>
VITE_USER_POOL_CLIENT_ID=<client-id>
VITE_AWS_REGION=us-east-1
```

### 5. Test

```bash
# Test API health endpoint
curl $(terraform output -raw api_url)/v1/health

# Test frontend
cd ../../src/frontend-react
npm run dev
```

## Common Issues

### Cognito Domain Already Exists

**Error**: `Domain already exists`

**Solution**: Change `cognito_domain_prefix` in `terraform.tfvars` to something unique.

### Lambda Package Too Large

**Error**: `RequestEntityTooLargeException`

**Solution**: 
- Check if dependencies are too large
- Consider using Lambda Layers (see `modules/lambda/main.tf`)
- Remove unnecessary files from package

### API Gateway Not Updating

**Issue**: Changes not reflected in API

**Solution**:
- Force redeployment by updating `modules/api_gateway/main.tf` triggers
- Or manually redeploy: `terraform taint module.api_gateway.aws_apigateway_deployment.main`

### State Lock Issues

**Error**: `Error acquiring the state lock`

**Solution**:
```bash
# If you're sure no one else is using it:
terraform force-unlock <lock-id>
```

## Comparing CDK vs Terraform

| Feature | CDK | Terraform |
|---------|-----|-----------|
| Language | TypeScript | HCL |
| State | CloudFormation | Local/S3 |
| Learning Curve | Steeper (TypeScript) | Gentler (HCL) |
| AWS Support | Good | Excellent |
| Error Messages | Sometimes unclear | Usually clear |
| Community | Growing | Very large |
| State Management | CloudFormation | Explicit files |

## After Migration

1. **Update CI/CD** (`.github/workflows/ci.yml`):
   - Replace `cdk deploy` with `terraform apply`
   - Update secrets if needed

2. **Update Documentation**:
   - Update `docs/DEPLOYMENT.md`
   - Update `README.md`

3. **Remove CDK** (optional):
   ```bash
   rm -rf infra/cdk
   ```

## Rollback Plan

If you need to rollback to CDK:

1. **Destroy Terraform resources:**
   ```bash
   cd infra/terraform
   terraform destroy
   ```

2. **Redeploy with CDK:**
   ```bash
   cd ../cdk
   cdk deploy
   ```

## Getting Help

- **Terraform Docs**: https://www.terraform.io/docs
- **AWS Provider Docs**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- **Terraform AWS Examples**: https://github.com/terraform-aws-modules

## Next Steps

1. ✅ Set up Terraform
2. ✅ Configure variables
3. ✅ Deploy infrastructure
4. ✅ Update frontend config
5. ✅ Test application
6. ⬜ Update CI/CD
7. ⬜ Update documentation
8. ⬜ Remove CDK (optional)

