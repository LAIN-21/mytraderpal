terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }

  # Optional: Configure remote state backend
  # Uncomment and configure for team collaboration
  # backend "s3" {
  #   bucket         = "mytraderpal-terraform-state"
  #   key            = "terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-state-lock"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "MyTraderPal"
      ManagedBy   = "Terraform"
      Environment = var.environment
    }
  }
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# DynamoDB Table
module "dynamodb" {
  source = "./modules/dynamodb"

  table_name = var.table_name
}

# Cognito User Pool
module "cognito" {
  source = "./modules/cognito"

  user_pool_name     = var.user_pool_name
  domain_prefix      = var.cognito_domain_prefix
  callback_urls      = var.cognito_callback_urls
  logout_urls        = var.cognito_logout_urls
  aws_account_id     = data.aws_caller_identity.current.account_id
}

# Lambda Function
module "lambda" {
  source = "./modules/lambda"

  function_name = var.lambda_function_name
  runtime       = var.lambda_runtime
  handler       = var.lambda_handler
  timeout       = var.lambda_timeout

  source_code_path = var.lambda_source_code_path
  requirements_path = var.lambda_requirements_path

  environment_variables = {
    TABLE_NAME = module.dynamodb.table_name
    DEV_MODE   = var.dev_mode
    AWS_REGION = var.aws_region
  }

  dynamodb_table_arn = module.dynamodb.table_arn
}

# API Gateway
module "api_gateway" {
  source = "./modules/api_gateway"

  api_name = var.api_name

  lambda_function_name = module.lambda.function_name
  lambda_invoke_arn    = module.lambda.invoke_arn

  cognito_user_pool_arn = module.cognito.user_pool_arn
  enable_cognito_auth   = var.enable_cognito_auth

  cors_allowed_origins = var.cors_allowed_origins
  cors_allowed_headers = var.cors_allowed_headers
  cors_allowed_methods = var.cors_allowed_methods
}

