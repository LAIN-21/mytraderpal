resource "aws_cognito_user_pool" "main" {
  name = var.user_pool_name

  # Sign-in configuration
  # Use username_attributes to allow email as username
  username_attributes = ["email"]

  # Auto-verify email
  auto_verified_attributes = ["email"]

  # Password policy
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_uppercase = true
    require_numbers   = true
    require_symbols   = true
  }

  # Account recovery
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  # Email configuration (uses Cognito default)
  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  # Schema
  schema {
    name                = "email"
    attribute_data_type = "String"
    required            = true
    mutable             = true
  }

  tags = {
    Name = var.user_pool_name
  }
}

resource "aws_cognito_user_pool_client" "main" {
  name         = "${var.user_pool_name}-client"
  user_pool_id = aws_cognito_user_pool.main.id

  generate_secret = false

  # Authentication flows
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]

  supported_identity_providers = ["COGNITO"]

  # OAuth configuration
  callback_urls = var.callback_urls
  logout_urls   = var.logout_urls

  allowed_oauth_flows = ["code"]
  allowed_oauth_scopes = [
    "email",
    "openid",
    "profile"
  ]
  allowed_oauth_flows_user_pool_client = true

  prevent_user_existence_errors = "ENABLED"
}

resource "aws_cognito_user_pool_domain" "main" {
  domain       = var.domain_prefix != "" ? var.domain_prefix : "mytraderpal-${var.aws_account_id}"
  user_pool_id = aws_cognito_user_pool.main.id
}

