variable "function_name" {
  description = "Lambda function name"
  type        = string
}

variable "handler" {
  description = "Lambda handler (e.g., 'app.main.handler')"
  type        = string
}

variable "timeout" {
  description = "Lambda timeout in seconds"
  type        = number
  default     = 30
}

variable "image_uri" {
  description = "ECR image URI for Lambda container image"
  type        = string
}

variable "environment_variables" {
  description = "Lambda environment variables"
  type        = map(string)
  default     = {}
}

variable "dynamodb_table_arn" {
  description = "DynamoDB table ARN"
  type        = string
}

