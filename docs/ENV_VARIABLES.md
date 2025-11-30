# Environment Variables in Terraform

With Terraform, all AWS infrastructure configuration and environment variables are managed in Terraform files.

## Configuration Flow

```
terraform.tfvars (your config)
    ↓
variables.tf (variable definitions)
    ↓
main.tf (creates resources with these values)
    ↓
outputs.tf (exports values for frontend)
```

## 1. Infrastructure Configuration (`terraform.tfvars`)

This is where you configure **how resources are created**:

```hcl
# AWS Configuration
aws_region  = "us-east-1"
environment = "dev"

# DynamoDB
table_name = "mtp_app"

# Cognito
user_pool_name        = "mytraderpal-users"
cognito_domain_prefix = "mytraderpal-dev-12345"  # Must be globally unique
cognito_callback_urls = ["http://localhost:3000/login"]
cognito_logout_urls   = ["http://localhost:3000/"]

# Lambda
lambda_function_name = "mytraderpal-api"
lambda_runtime       = "python3.11"
lambda_handler       = "main.handler"
lambda_timeout       = 30

# Development Mode
dev_mode          = "true"  # Set to "false" for production
enable_cognito_auth = false  # Set to true when dev_mode is false
```

## 2. Lambda Runtime Environment Variables (`main.tf`)

These are the environment variables **available to your Lambda function at runtime**:

```hcl
module "lambda" {
  # ...
  environment_variables = {
    TABLE_NAME = module.dynamodb.table_name  # From DynamoDB module
    DEV_MODE   = var.dev_mode                 # From terraform.tfvars
    AWS_REGION = var.aws_region               # From terraform.tfvars
  }
}
```

These map to what your Python code reads:
- `os.getenv('TABLE_NAME')` → Gets value from Terraform
- `os.getenv('DEV_MODE')` → Gets value from Terraform
- `os.getenv('AWS_REGION')` → Gets value from Terraform

## 3. Terraform Outputs (`outputs.tf`)

After deployment, Terraform outputs values you need for frontend configuration:

```bash
terraform output
```

Outputs:
- `api_url` → Use in frontend `VITE_API_URL`
- `user_pool_id` → Use in frontend `VITE_USER_POOL_ID`
- `user_pool_client_id` → Use in frontend `VITE_USER_POOL_CLIENT_ID`
- `cognito_domain` → Cognito domain name
- `table_name` → DynamoDB table name

## 4. Frontend Configuration (`src/frontend-react/.env`)

After Terraform deployment, update frontend `.env` with Terraform outputs:

```env
VITE_API_URL=https://xxxxx.execute-api.us-east-1.amazonaws.com/prod
VITE_USER_POOL_ID=us-east-1_xxxxx
VITE_USER_POOL_CLIENT_ID=xxxxx
VITE_AWS_REGION=us-east-1
```

## Workflow

1. **Configure Terraform** (`terraform.tfvars`):
   ```bash
   cd infra/terraform
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars
   ```

2. **Deploy Infrastructure**:
   ```bash
   terraform init
   terraform apply
   ```

3. **Get Outputs**:
   ```bash
   terraform output
   ```

4. **Update Frontend**:
   ```bash
   # Copy outputs to src/frontend-react/.env
   VITE_API_URL=$(terraform output -raw api_url)
   VITE_USER_POOL_ID=$(terraform output -raw user_pool_id)
   # etc.
   ```

## Key Points

✅ **Infrastructure config** → `terraform.tfvars`  
✅ **Lambda env vars** → Set in `main.tf` (environment_variables block)  
✅ **Cognito config** → Set in `terraform.tfvars`  
✅ **Outputs** → Use `terraform output` to get values for frontend  
✅ **Frontend config** → Update `.env` with Terraform outputs  

## Local Development vs Production

### Local Development (Docker)
- Uses `src/app/.env` for Lambda env vars
- Uses `src/frontend-react/.env` for frontend
- No Terraform needed for local dev

### Production (AWS)
- Lambda env vars come from Terraform (`main.tf`)
- Frontend env vars come from Terraform outputs
- Everything configured in `terraform.tfvars`

## Adding New Environment Variables

1. **For Lambda**: Add to `environment_variables` in `main.tf`:
   ```hcl
   environment_variables = {
     TABLE_NAME = module.dynamodb.table_name
     DEV_MODE   = var.dev_mode
     AWS_REGION = var.aws_region
     NEW_VAR    = var.new_var  # Add here
   }
   ```

2. **Add variable definition** in `variables.tf`:
   ```hcl
   variable "new_var" {
     description = "Description"
     type        = string
     default     = "default_value"
   }
   ```

3. **Set value** in `terraform.tfvars`:
   ```hcl
   new_var = "your_value"
   ```

4. **Use in code**: `os.getenv('NEW_VAR')`

