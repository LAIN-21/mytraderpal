# MyTraderPal

A trading journal and strategy testing application for traders.

## Architecture

- **Frontend**: Next.js (TypeScript) + Tailwind + shadcn/ui, hosted on AWS Amplify
- **Auth**: Amazon Cognito (Hosted UI → ID Token/JWT)
- **API**: API Gateway (HTTP) + Lambda (Python) running FastAPI via Mangum
- **DB**: DynamoDB single-table design
- **IaC**: AWS CDK (TypeScript)

## Project Structure

```
mytraderpal/
├── cdk/                    # CDK app (TypeScript)
│   ├── bin/
│   ├── lib/
│   └── package.json
├── frontend/               # Next.js app
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
├── services/
│   └── api/                # FastAPI + Mangum for Lambda
│       ├── main.py
│       ├── requirements.txt
│       └── common/
└── README.md
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.12+
- AWS CLI configured
- AWS CDK installed (`npm install -g aws-cdk`)

### Development Setup

1. **CDK Setup**:
   ```bash
   cd cdk
   npm install
   cdk bootstrap
   cdk deploy
   ```

2. **Backend Setup**:
   ```bash
   cd services/api
   pip install -r requirements.txt
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_AWS_REGION=<region>
NEXT_PUBLIC_API_URL=https://<api-id>.execute-api.<region>.amazonaws.com
NEXT_PUBLIC_USER_POOL_ID=<cdk output>
NEXT_PUBLIC_USER_POOL_CLIENT_ID=<cdk output>
NEXT_PUBLIC_COGNITO_DOMAIN=<domain>.auth.<region>.amazoncognito.com
NEXT_PUBLIC_OAUTH_REDIRECT=https://<amplify-domain>.amplifyapp.com/login
```

### Backend (Lambda env)
```
TABLE_NAME=mtp_app
DEV_MODE=false
```

## Features (MVP)

- ✅ Authentication (Cognito Hosted UI)
- ✅ Trade Journal (CRUD)
- ✅ Strategies (CRUD)
- 🔄 Strategy Testing (Future)

## DynamoDB Design

Single table: `mtp_app`
- **Keys**: PK (partition), SK (sort)
- **GSI1**: GSI1PK, GSI1SK (listing)

### Entities

**User Profile**: `PK=USER#<userId>`, `SK=PROFILE#<userId>`

**Notes**: `PK=USER#<userId>`, `SK=NOTE#<noteId>`
- Attributes: entityType="NOTE", date(ISO), text, direction?, session?, risk?, win_amount?, tags?[], strategyId?, createdAt, updatedAt
- GSI1: `GSI1PK=NOTE#<userId>`, `GSI1SK=<date>#<noteId>`

**Strategies**: `PK=USER#<userId>`, `SK=STRAT#<strategyId>`
- Attributes: entityType="STRATEGY", name, market, timeframe, dsl(obj), createdAt, updatedAt
- GSI1: `GSI1PK=STRAT#<userId>`, `GSI1SK=<createdAt>#<strategyId>`
