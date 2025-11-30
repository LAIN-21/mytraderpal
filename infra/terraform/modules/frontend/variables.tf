variable "bucket_name" {
  description = "S3 bucket name for frontend hosting"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

