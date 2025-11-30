# Build Lambda package with dependencies
resource "null_resource" "lambda_package" {
  triggers = {
    source_code_hash = sha256(join("", [
      for f in fileset(var.source_code_path, "**") : filesha256("${var.source_code_path}/${f}")
    ]))
    requirements_hash = filemd5(var.requirements_path)
  }

  provisioner "local-exec" {
    command = <<-EOT
      set -e
      PACKAGE_DIR="${path.module}/.lambda_package"
      rm -rf "$PACKAGE_DIR"
      mkdir -p "$PACKAGE_DIR"
      
      # Copy source code
      cp -r ${var.source_code_path}/* "$PACKAGE_DIR/" 2>/dev/null || true
      
      # Install dependencies
      pip install -r ${var.requirements_path} -t "$PACKAGE_DIR" --quiet --disable-pip-version-check
      
      # Remove unnecessary files
      find "$PACKAGE_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
      find "$PACKAGE_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
    EOT
  }
}

# Archive Lambda package
data "archive_file" "lambda_zip" {
  depends_on  = [null_resource.lambda_package]
  type        = "zip"
  source_dir  = "${path.module}/.lambda_package"
  output_path = "${path.module}/lambda_package.zip"
  excludes    = ["__pycache__", "*.pyc", ".pytest_cache", "*.dist-info", "*.egg-info"]
}

# Lambda Function
resource "aws_lambda_function" "main" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = var.function_name
  role            = aws_iam_role.lambda.arn
  handler         = var.handler
  runtime         = var.runtime
  timeout         = var.timeout
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = var.environment_variables
  }

  tags = {
    Name = var.function_name
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda" {
  name = "${var.function_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda (CloudWatch Logs)
resource "aws_iam_role_policy" "lambda_logs" {
  name = "${var.function_name}-logs"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# IAM Policy for Lambda (DynamoDB)
resource "aws_iam_role_policy" "lambda_dynamodb" {
  name = "${var.function_name}-dynamodb"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          var.dynamodb_table_arn,
          "${var.dynamodb_table_arn}/index/*"
        ]
      }
    ]
  })
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = 7
}

