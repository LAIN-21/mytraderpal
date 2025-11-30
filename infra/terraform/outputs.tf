output "api_url" {
  description = "API Gateway URL"
  value       = module.api_gateway.api_url
}

output "user_pool_id" {
  description = "Cognito User Pool ID"
  value       = module.cognito.user_pool_id
}

output "user_pool_client_id" {
  description = "Cognito User Pool Client ID"
  value       = module.cognito.user_pool_client_id
}

output "cognito_domain" {
  description = "Cognito Domain"
  value       = module.cognito.domain_name
}

output "table_name" {
  description = "DynamoDB Table Name"
  value       = module.dynamodb.table_name
}

output "lambda_function_name" {
  description = "Lambda Function Name"
  value       = module.lambda.function_name
}

output "lambda_function_arn" {
  description = "Lambda Function ARN"
  value       = module.lambda.function_arn
}

output "ecr_repository_url" {
  description = "ECR Repository URL for Lambda container images"
  value       = module.ecr.repository_url
}

output "ecr_repository_name" {
  description = "ECR Repository Name"
  value       = module.ecr.repository_name
}

output "frontend_url" {
  description = "Frontend CloudFront URL"
  value       = module.frontend.cloudfront_url
}

output "frontend_bucket_name" {
  description = "Frontend S3 Bucket Name"
  value       = module.frontend.bucket_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront Distribution ID"
  value       = module.frontend.cloudfront_distribution_id
}

