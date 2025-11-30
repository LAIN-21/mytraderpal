# MyTraderPal Terraform Infrastructure

This directory contains Terraform configuration for deploying MyTraderPal infrastructure to AWS.

## Prerequisites

1. **Terraform** >= 1.5.0 installed
   ```bash
   brew install terraform  # macOS
   # or download from https://www.terraform.io/downloads
   ```

2. **AWS CLI** configured with credentials
   ```bash
   aws configure
   ```

3. **Python 3.11+** and `pip` (for Lambda dependencies)

4. **AWS Account** with appropriate permissions

## Quick Start

1. **Copy the example variables file:**
   ```bash
   cd infra/terraform
   cp terraform.tfvars.example terraform.tfvars
   ```

2. **Edit `terraform.tfvars`** with your configuration:
   ```hcl
   aws_region  = "us-east-1"
   environment = "dev"
   cognito_domain_prefix = "mytraderpal-dev-12345"  # Must be globally unique
   ```

3. **Initialize Terraform:**
   ```bash
   terraform init
   ```

4. **Review the plan:**
   ```bash
   terraform plan
   ```

5. **Apply the configuration:**
   ```bash
   terraform apply
   ```

6. **Get outputs:**
   ```bash
   terraform output
   ```

## Configuration

### Variables

Key variables in `terraform.tfvars`:

- `aws_region`: AWS region (default: `us-east-1`)
- `environment`: Environment name (default: `dev`)
- `cognito_domain_prefix`: Must be globally unique across all AWS accounts
- `dev_mode`: Set to `"true"` for development (bypasses auth)
- `enable_cognito_auth`: Set to `true` when `dev_mode` is `false`

### Outputs

After deployment, Terraform outputs:

- `api_url`: API Gateway URL
- `user_pool_id`: Cognito User Pool ID
- `user_pool_client_id`: Cognito User Pool Client ID
- `cognito_domain`: Cognito domain name
- `table_name`: DynamoDB table name

## Architecture

The infrastructure consists of:

1. **DynamoDB Table** (`mtp_app`)
   - Partition key: `PK`
   - Sort key: `SK`
   - GSI1: `GSI1PK` / `GSI1SK`

2. **Cognito User Pool**
   - User authentication
   - OAuth 2.0 flows
   - Email verification

3. **Lambda Function**
   - Python 3.11 runtime
   - Handles all API requests
   - Connected to DynamoDB

4. **API Gateway**
   - REST API
   - CORS enabled
   - Optional Cognito authorizer

## Modules

- `modules/dynamodb`: DynamoDB table configuration
- `modules/cognito`: Cognito User Pool, Client, and Domain
- `modules/lambda`: Lambda function with dependencies
- `modules/api_gateway`: API Gateway with CORS and authorizer

## Updating Infrastructure

1. **Make changes** to `.tf` files
2. **Review plan:**
   ```bash
   terraform plan
   ```
3. **Apply changes:**
   ```bash
   terraform apply
   ```

## Destroying Infrastructure

⚠️ **Warning**: This will delete all resources!

```bash
terraform destroy
```

## Troubleshooting

### Lambda Package Issues

If Lambda deployment fails:

1. Check Python version matches runtime:
   ```bash
   python3 --version  # Should be 3.11+
   ```

2. Verify dependencies install correctly:
   ```bash
   pip install -r ../../requirements.txt -t test_package/
   ```

### Cognito Domain Already Exists

Cognito domain prefixes must be globally unique. If you get an error:

1. Change `cognito_domain_prefix` in `terraform.tfvars`
2. Run `terraform apply` again

### API Gateway Not Updating

If API Gateway changes aren't reflected:

1. Check deployment status:
   ```bash
   terraform refresh
   terraform plan
   ```

2. Force redeployment by updating a trigger in `modules/api_gateway/main.tf`

## State Management

### Local State (Default)

State is stored locally in `terraform.tfstate`. This is fine for single-user development.

### Remote State (Recommended for Teams)

Uncomment the `backend` block in `main.tf` and configure S3 backend:

```hcl
backend "s3" {
  bucket         = "mytraderpal-terraform-state"
  key            = "terraform.tfstate"
  region         = "us-east-1"
  encrypt        = true
  dynamodb_table = "terraform-state-lock"
}
```

Then create the S3 bucket and DynamoDB table for state locking.

## Migration from CDK

If migrating from CDK:

1. **Export existing resources** (optional):
   ```bash
   cd infra/cdk
   cdk synth > cdk-output.json
   ```

2. **Import existing resources** into Terraform:
   ```bash
   terraform import aws_dynamodb_table.main mtp_app
   terraform import aws_cognito_user_pool.main <user-pool-id>
   # ... etc
   ```

3. **Or start fresh** by destroying CDK stack first:
   ```bash
   cd infra/cdk
   cdk destroy
   ```

## CI/CD Integration

See `.github/workflows/ci.yml` for GitHub Actions integration example.

## Security Notes

- Never commit `terraform.tfvars` with sensitive data
- Use AWS Secrets Manager for production secrets
- Enable MFA for AWS accounts
- Use least-privilege IAM policies

