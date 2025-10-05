# MyTraderPal Deployment Guide

This guide will walk you through deploying the MyTraderPal application to AWS.

## Prerequisites

1. **AWS CLI configured** with appropriate permissions
2. **Node.js 18+** and **npm**
3. **Python 3.12+** and **pip**
4. **AWS CDK** installed globally: `npm install -g aws-cdk`

## Step 1: Deploy Infrastructure (CDK)

1. **Navigate to CDK directory**:
   ```bash
   cd cdk
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Bootstrap CDK** (first time only):
   ```bash
   cdk bootstrap
   ```

4. **Deploy the stack**:
   ```bash
   cdk deploy
   ```

5. **Note the outputs** from the deployment:
   - `ApiUrl`: Your API Gateway URL
   - `UserPoolId`: Cognito User Pool ID
   - `UserPoolClientId`: Cognito User Pool Client ID
   - `CognitoDomain`: Cognito domain name
   - `TableName`: DynamoDB table name

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

4. **Update `.env.local`** with the values from CDK deployment:
   ```env
   NEXT_PUBLIC_AWS_REGION=us-east-1
   NEXT_PUBLIC_API_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com
   NEXT_PUBLIC_USER_POOL_ID=us-east-1_xxxxxxxxx
   NEXT_PUBLIC_USER_POOL_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
   NEXT_PUBLIC_COGNITO_DOMAIN=mytraderpal-xxxxxxxxx.auth.us-east-1.amazoncognito.com
   NEXT_PUBLIC_OAUTH_REDIRECT=http://localhost:3000/login
   ```

5. **Start development server**:
   ```bash
   npm run dev
   ```

## Step 3: Deploy Frontend to AWS Amplify

1. **Connect your repository** to AWS Amplify Hosting
2. **Set build settings**:
   - Build command: `npm run build`
   - Base directory: `frontend`
   - Output directory: `.next`

3. **Set environment variables** in Amplify console:
   - `NEXT_PUBLIC_AWS_REGION`
   - `NEXT_PUBLIC_API_URL`
   - `NEXT_PUBLIC_USER_POOL_ID`
   - `NEXT_PUBLIC_USER_POOL_CLIENT_ID`
   - `NEXT_PUBLIC_COGNITO_DOMAIN`
   - `NEXT_PUBLIC_OAUTH_REDIRECT` (update to your Amplify domain)

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
