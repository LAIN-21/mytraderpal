#!/bin/bash
# Setup Terraform remote state backend (S3 + DynamoDB)

set -e

# Configuration
BUCKET_NAME="mytraderpal-terraform-state"
DYNAMODB_TABLE="terraform-state-lock"
REGION="${AWS_REGION:-us-east-1}"

echo "🔧 Setting up Terraform remote state backend..."
echo ""

# Check AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Error: AWS CLI is not configured"
    echo "   Run: aws configure"
    exit 1
fi

echo "✅ AWS CLI is configured"
echo ""

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "📋 AWS Account ID: $AWS_ACCOUNT_ID"
echo "📋 Region: $REGION"
echo ""

# Create S3 bucket for Terraform state
echo "📦 Creating S3 bucket for Terraform state..."
if aws s3 ls "s3://${BUCKET_NAME}" 2>&1 | grep -q 'NoSuchBucket'; then
    aws s3 mb "s3://${BUCKET_NAME}" --region "$REGION"
    echo "✅ S3 bucket created: ${BUCKET_NAME}"
else
    echo "⚠️  S3 bucket already exists: ${BUCKET_NAME}"
fi

# Enable versioning
echo "📦 Enabling versioning on S3 bucket..."
aws s3api put-bucket-versioning \
    --bucket "$BUCKET_NAME" \
    --versioning-configuration Status=Enabled \
    --region "$REGION"
echo "✅ Versioning enabled"

# Enable encryption
echo "📦 Enabling encryption on S3 bucket..."
aws s3api put-bucket-encryption \
    --bucket "$BUCKET_NAME" \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }' \
    --region "$REGION"
echo "✅ Encryption enabled"

# Block public access
echo "📦 Blocking public access..."
aws s3api put-public-access-block \
    --bucket "$BUCKET_NAME" \
    --public-access-block-configuration \
        "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true" \
    --region "$REGION"
echo "✅ Public access blocked"

echo ""

# Create DynamoDB table for state locking
echo "🔒 Creating DynamoDB table for state locking..."
if aws dynamodb describe-table --table-name "$DYNAMODB_TABLE" --region "$REGION" &> /dev/null; then
    echo "⚠️  DynamoDB table already exists: ${DYNAMODB_TABLE}"
else
    aws dynamodb create-table \
        --table-name "$DYNAMODB_TABLE" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --region "$REGION" \
        --tags Key=Name,Value=TerraformStateLock Key=Project,Value=MyTraderPal
    
    echo "⏳ Waiting for table to be active..."
    aws dynamodb wait table-exists --table-name "$DYNAMODB_TABLE" --region "$REGION"
    echo "✅ DynamoDB table created: ${DYNAMODB_TABLE}"
fi

echo ""
echo "✅ Terraform remote state backend setup complete!"
echo ""
echo "📋 Summary:"
echo "  S3 Bucket: ${BUCKET_NAME}"
echo "  DynamoDB Table: ${DYNAMODB_TABLE}"
echo "  Region: ${REGION}"
echo ""
echo "📝 Next steps:"
echo "  1. Update infra/terraform/main.tf to uncomment backend block"
echo "  2. Run: cd infra/terraform && terraform init"
echo "  3. Terraform will ask to migrate state - type 'yes'"
echo ""

