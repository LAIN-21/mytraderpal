variable "user_pool_name" {
  description = "Cognito User Pool name"
  type        = string
}

variable "domain_prefix" {
  description = "Cognito domain prefix (optional, will use account ID if not provided)"
  type        = string
  default     = ""
}

variable "aws_account_id" {
  description = "AWS Account ID"
  type        = string
}

variable "callback_urls" {
  description = "OAuth callback URLs"
  type        = list(string)
  default     = []
}

variable "logout_urls" {
  description = "OAuth logout URLs"
  type        = list(string)
  default     = []
}

