# API Gateway REST API
resource "aws_apigateway_rest_api" "main" {
  name        = var.api_name
  description = "MyTraderPal API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# API Gateway Resource (v1)
resource "aws_apigateway_resource" "v1" {
  rest_api_id = aws_apigateway_rest_api.main.id
  parent_id   = aws_apigateway_rest_api.main.root_resource_id
  path_part   = "v1"
}

# API Gateway Resource (proxy)
resource "aws_apigateway_resource" "proxy" {
  rest_api_id = aws_apigateway_rest_api.main.id
  parent_id   = aws_apigateway_resource.v1.id
  path_part   = "{proxy+}"
}

# API Gateway Method (ANY)
resource "aws_apigateway_method" "proxy" {
  rest_api_id   = aws_apigateway_rest_api.main.id
  resource_id   = aws_apigateway_resource.proxy.id
  http_method   = "ANY"
  authorization = var.enable_cognito_auth ? "COGNITO_USER_POOLS" : "NONE"
  authorizer_id = var.enable_cognito_auth ? aws_apigateway_authorizer.cognito[0].id : null
}

# Cognito Authorizer (optional)
resource "aws_apigateway_authorizer" "cognito" {
  count           = var.enable_cognito_auth ? 1 : 0
  name            = "CognitoAuthorizer"
  type            = "COGNITO_USER_POOLS"
  rest_api_id     = aws_apigateway_rest_api.main.id
  provider_arns   = [var.cognito_user_pool_arn]
  identity_source = "method.request.header.Authorization"
}

# API Gateway Integration
resource "aws_apigateway_integration" "lambda" {
  rest_api_id = aws_apigateway_rest_api.main.id
  resource_id = aws_apigateway_resource.proxy.id
  http_method = aws_apigateway_method.proxy.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

# API Gateway Method Response
resource "aws_apigateway_method_response" "proxy" {
  rest_api_id = aws_apigateway_rest_api.main.id
  resource_id = aws_apigateway_resource.proxy.id
  http_method = aws_apigateway_method.proxy.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

# API Gateway Integration Response
resource "aws_apigateway_integration_response" "proxy" {
  rest_api_id = aws_apigateway_rest_api.main.id
  resource_id = aws_apigateway_resource.proxy.id
  http_method = aws_apigateway_method.proxy.http_method
  status_code = aws_apigateway_method_response.proxy.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
  }

  depends_on = [aws_apigateway_integration.lambda]
}

# OPTIONS method for CORS preflight
resource "aws_apigateway_method" "options" {
  rest_api_id   = aws_apigateway_rest_api.main.id
  resource_id   = aws_apigateway_resource.proxy.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_apigateway_integration" "options" {
  rest_api_id = aws_apigateway_rest_api.main.id
  resource_id = aws_apigateway_resource.proxy.id
  http_method = aws_apigateway_method.options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_apigateway_method_response" "options" {
  rest_api_id = aws_apigateway_rest_api.main.id
  resource_id = aws_apigateway_resource.proxy.id
  http_method = aws_apigateway_method.options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_apigateway_integration_response" "options" {
  rest_api_id = aws_apigateway_rest_api.main.id
  resource_id = aws_apigateway_resource.proxy.id
  http_method = aws_apigateway_method.options.http_method
  status_code = aws_apigateway_method_response.options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'${join(",", var.cors_allowed_headers)}'"
    "method.response.header.Access-Control-Allow-Methods" = "'${join(",", var.cors_allowed_methods)}'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }

  depends_on = [aws_apigateway_integration.options]
}

# Lambda Permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigateway_rest_api.main.execution_arn}/*/*"
}

# API Gateway Deployment
resource "aws_apigateway_deployment" "main" {
  depends_on = [
    aws_apigateway_integration.lambda,
    aws_apigateway_integration.options,
  ]

  rest_api_id = aws_apigateway_rest_api.main.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_apigateway_resource.proxy.id,
      aws_apigateway_method.proxy.id,
      aws_apigateway_integration.lambda.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

# API Gateway Stage
resource "aws_apigateway_stage" "main" {
  deployment_id = aws_apigateway_deployment.main.id
  rest_api_id   = aws_apigateway_rest_api.main.id
  stage_name    = "prod"
}

