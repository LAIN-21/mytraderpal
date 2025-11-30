#!/bin/bash
# Deploy infrastructure using Terraform

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="${SCRIPT_DIR}/../infra/terraform"

echo "🚀 Deploying MyTraderPal infrastructure with Terraform..."
echo ""

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "❌ Error: Terraform is not installed"
    echo "   Install from: https://www.terraform.io/downloads"
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Error: AWS CLI is not configured"
    echo "   Run: aws configure"
    exit 1
fi

cd "$TERRAFORM_DIR"

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    echo "⚠️  Warning: terraform.tfvars not found"
    echo "   Copying from terraform.tfvars.example..."
    cp terraform.tfvars.example terraform.tfvars
    echo "   Please edit terraform.tfvars before continuing"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to cancel..."
fi

# Initialize Terraform
echo "📦 Initializing Terraform..."
terraform init

# Plan
echo ""
echo "📋 Planning infrastructure changes..."
terraform plan

# Confirm
echo ""
read -p "Apply these changes? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ Deployment cancelled"
    exit 0
fi

# Apply
echo ""
echo "🚀 Applying infrastructure changes..."
terraform apply -auto-approve

# Outputs
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Infrastructure outputs:"
terraform output

echo ""
echo "💡 Next steps:"
echo "   1. Update frontend .env with the outputs above"
echo "   2. Test the API: curl \$(terraform output -raw api_url)/v1/health"
echo ""

