# MyTraderPal

A trading journal application for tracking trades, strategies, and market observations.

## What it does

- **Trading Journal**: Record daily trading notes with direction, session, risk/win amounts, and strategy tracking
- **Strategy Management**: Create and manage trading strategies with market and timeframe specifications
- **Hit/Miss Tracking**: Track whether your trades hit or miss your strategy targets

## Tech Stack

- **Frontend**: Next.js + TypeScript + Tailwind CSS
- **Backend**: AWS Lambda + Python
- **Database**: AWS DynamoDB
- **Authentication**: AWS Cognito
- **Infrastructure**: AWS CDK

## Setup & Installation

### Prerequisites
- Node.js 18+
- Python 3.11+
- AWS CLI configured
- AWS CDK installed: `npm install -g aws-cdk`

### 1. Deploy Infrastructure
```bash
cd cdk
npm install
cdk bootstrap
cdk deploy MyTraderPalStack
```

### 2. Setup Frontend
```bash
cd frontend
npm install
```

Copy the CDK outputs to create `.env.local`:
```bash
NEXT_PUBLIC_AWS_REGION=us-east-1
NEXT_PUBLIC_API_URL=https://[your-api-url]
NEXT_PUBLIC_USER_POOL_ID=[cdk-output]
NEXT_PUBLIC_USER_POOL_CLIENT_ID=[cdk-output]
NEXT_PUBLIC_COGNITO_DOMAIN=[cdk-output]
```

### 3. Run Frontend
```bash
npm run dev
```

Visit `http://localhost:3000` and start using the app!

## Features

- ✅ User authentication with AWS Cognito
- ✅ Trading notes with date, direction, session, risk/win tracking
- ✅ Strategy creation and management
- ✅ Hit/miss trade result tracking
- ✅ Responsive design with clean UI

## Development

The app runs in development mode with `DEV_MODE=true`, allowing API testing without authentication. Switch to production mode by setting `DEV_MODE=false` in the CDK stack.