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

