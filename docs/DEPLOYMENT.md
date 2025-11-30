# MyTraderPal Deployment Guide

This guide will walk you through deploying the MyTraderPal application to AWS.

## Prerequisites

1. **AWS CLI configured** with appropriate permissions
2. **Terraform** >= 1.5.0 installed
3. **Python 3.11+** and **pip** (for Lambda dependencies)

## Step 1: Deploy Infrastructure (Terraform)

### Option 1: Using Make (Recommended)

```bash
make deploy
```

This will:
- Check prerequisites
- Initialize Terraform
- Show plan
- Apply changes
- Display outputs

### Option 2: Manual Deployment

1. **Navigate to Terraform directory**:
   ```bash
   cd infra/terraform
   ```

2. **Copy and configure variables**:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your configuration
   ```

3. **Initialize Terraform**:
   ```bash
   terraform init
   ```

4. **Review the plan**:
   ```bash
   terraform plan
   ```

5. **Deploy the infrastructure**:
   ```bash
   terraform apply
   ```

6. **Get outputs**:
   ```bash
   terraform output
   ```

   Outputs include:
   - `api_url`: Your API Gateway URL
   - `user_pool_id`: Cognito User Pool ID
   - `user_pool_client_id`: Cognito User Pool Client ID
   - `cognito_domain`: Cognito domain name
   - `table_name`: DynamoDB table name

## Step 2: Configure Frontend

1. **Navigate to frontend directory**:
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Create environment file**:
   ```bash
   cp env.example .env.local
   ```

4. **Update `.env`** with the values from CDK deployment:
   ```env
   VITE_AWS_REGION=us-east-1
   VITE_API_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com
   VITE_USER_POOL_ID=us-east-1_xxxxxxxxx
   VITE_USER_POOL_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

5. **Start development server**:
   ```bash
   npm run dev
   ```

## Step 3: Deploy Frontend to AWS Amplify

1. **Connect your repository** to AWS Amplify Hosting (or use Docker deployment)
2. **Set build settings** (if using Amplify):
   - Build command: `npm run build`
   - Base directory: `src/frontend-react`
   - Output directory: `dist`

3. **Set environment variables** in deployment platform:
   - `VITE_AWS_REGION`
   - `VITE_API_URL`
   - `VITE_USER_POOL_ID`
   - `VITE_USER_POOL_CLIENT_ID`

4. **Update Cognito OAuth settings**:
   - Go to Cognito User Pool in AWS Console
   - Update callback URLs to include your Amplify domain
   - Update logout URLs to include your Amplify domain

## Step 4: Test the Application

1. **Visit your Amplify domain**
2. **Sign up** for a new account
3. **Test the features**:
   - Create trading notes
   - Create trading strategies
   - Edit and delete items

## Development Mode

For local development with authentication bypass:

1. **Set environment variable** in Lambda:
   ```bash
   aws lambda update-function-configuration \
     --function-name MyTraderPalStack-ApiFunction-xxxxx \
     --environment Variables='{TABLE_NAME=mtp_app,DEV_MODE=true}'
   ```

2. **Add header** to API requests:
   ```
   X-MTP-Dev-User: dev
   ```

## Troubleshooting

### Common Issues

1. **CORS errors**: Ensure your Amplify domain is added to CORS origins in CDK
2. **Authentication errors**: Check that environment variables are set correctly
3. **API errors**: Verify the API Gateway URL and Lambda function logs

### Useful Commands

```bash
# View CDK stack outputs
cdk list

# Destroy stack (careful!)
cdk destroy

# View Lambda logs
aws logs tail /aws/lambda/MyTraderPalStack-ApiFunction-xxxxx --follow

# Test API directly
curl -X GET https://your-api-url/v1/health
```

## Security Considerations

1. **Tighten CORS** to your specific domain in production
2. **Enable CloudTrail** for audit logging
3. **Set up monitoring** with CloudWatch alarms
4. **Regular security reviews** of IAM permissions

## Cost Optimization

1. **DynamoDB**: Uses on-demand billing (pay per request)
2. **Lambda**: Pay per invocation
3. **API Gateway**: Pay per request
4. **Cognito**: Free tier includes 50,000 MAUs

Monitor usage in AWS Cost Explorer and set up billing alerts.
