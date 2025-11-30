variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "table_name" {
  description = "DynamoDB table name"
  type        = string
  default     = "mtp_app"
}

variable "user_pool_name" {
  description = "Cognito User Pool name"
  type        = string
  default     = "mytraderpal-users"
}

variable "cognito_domain_prefix" {
  description = "Cognito domain prefix (must be globally unique)"
  type        = string
  default     = ""
}

variable "cognito_callback_urls" {
  description = "Cognito OAuth callback URLs"
  type        = list(string)
  default = [
    "http://localhost:3000/login",
    "https://*.amplifyapp.com/login"
  ]
}

variable "cognito_logout_urls" {
  description = "Cognito OAuth logout URLs"
  type        = list(string)
  default = [
    "http://localhost:3000/",
    "https://*.amplifyapp.com/"
  ]
}

variable "lambda_function_name" {
  description = "Lambda function name"
  type        = string
  default     = "mytraderpal-api"
}

variable "lambda_handler" {
  description = "Lambda handler (for container images, this is the CMD)"
  type        = string
  default     = "app.main.handler"
}

variable "lambda_image_uri" {
  description = "Lambda container image URI (if empty, uses ECR repo with 'latest' tag)"
  type        = string
  default     = ""
}

variable "lambda_timeout" {
  description = "Lambda timeout in seconds"
  type        = number
  default     = 30
}


variable "api_name" {
  description = "API Gateway name"
  type        = string
  default     = "mytraderpal-api"
}

variable "dev_mode" {
  description = "Enable development mode (bypasses Cognito auth)"
  type        = string
  default     = "true"
}

variable "enable_cognito_auth" {
  description = "Enable Cognito authorization on API Gateway"
  type        = bool
  default     = false
}

variable "cors_allowed_origins" {
  description = "CORS allowed origins"
  type        = list(string)
  default = [
    "http://localhost:3000",
    "https://*.amplifyapp.com"
  ]
}

variable "cors_allowed_headers" {
  description = "CORS allowed headers"
  type        = list(string)
  default = [
    "Content-Type",
    "Authorization",
    "X-MTP-Dev-User"
  ]
}

variable "cors_allowed_methods" {
  description = "CORS allowed methods"
  type        = list(string)
  default     = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
}

variable "frontend_bucket_name" {
  description = "S3 bucket name for frontend hosting"
  type        = string
  default     = "mytraderpal-frontend"
}

