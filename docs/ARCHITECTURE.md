# MyTraderPal Architecture

## Overview

MyTraderPal is a serverless trading journal application built on AWS with a modern layered architecture.

## High-Level Architecture

```
┌─────────────────┐
│   Frontend      │
│   (Next.js)     │
│   Port: 3000    │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  API Gateway    │
│  (REST API)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│   Lambda        │─────▶│  DynamoDB    │
│   (Python 3.11) │      │  (Single     │
│                 │      │   Table)     │
└─────────────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐
│   Cognito       │
│   (Auth)        │
└─────────────────┘
```

## Application Architecture (Layered)

```
┌─────────────────────────────────────────┐
│           API Layer (Controllers)      │
│  - notes.py, strategies.py, reports.py │
│  - Handles HTTP requests/responses      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Service Layer (Business Logic)  │
│  - note_service.py                      │
│  - strategy_service.py                  │
│  - report_service.py                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Repository Layer (Data Access)     │
│  - dynamodb.py                          │
│  - Abstracts database operations        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│           DynamoDB                      │
│  - Single-table design                  │
│  - GSI1 for queries                    │
└─────────────────────────────────────────┘
```

## Component Diagram

```
┌──────────────┐
│   Frontend    │
│  (Next.js)   │
└──────┬───────┘
       │
       │ REST API
       ▼
┌──────────────────────────────────────┐
│         API Gateway                  │
│  ┌────────────────────────────────┐  │
│  │  Lambda Handler (main.py)      │  │
│  │  ┌──────────────────────────┐  │  │
│  │  │  Router (router.py)      │  │  │
│  │  └──────────┬───────────────┘  │  │
│  │             │                   │  │
│  │  ┌──────────▼───────────────┐  │  │
│  │  │  Controllers (api/)      │  │  │
│  │  │  - notes.py              │  │  │
│  │  │  - strategies.py         │  │  │
│  │  │  - reports.py            │  │  │
│  │  │  - metrics.py            │  │  │
│  │  └──────────┬───────────────┘  │  │
│  │             │                   │  │
│  │  ┌──────────▼───────────────┐  │  │
│  │  │  Services (services/)    │  │  │
│  │  │  - note_service.py        │  │  │
│  │  │  - strategy_service.py    │  │  │
│  │  │  - report_service.py      │  │  │
│  │  └──────────┬───────────────┘  │  │
│  │             │                   │  │
│  │  ┌──────────▼───────────────┐  │  │
│  │  │  Repositories            │  │  │
│  │  │  - dynamodb.py           │  │  │
│  │  └──────────┬───────────────┘  │  │
│  └─────────────┼───────────────────┘  │
└────────────────┼──────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │   DynamoDB    │
         │  Single Table │
         │  + GSI1       │
         └───────────────┘
```

## Data Model

### DynamoDB Single-Table Design

**Primary Key Structure:**
- `PK`: Partition Key (e.g., `USER#user123`)
- `SK`: Sort Key (e.g., `NOTE#note456`)

**GSI1 (Global Secondary Index):**
- `GSI1PK`: Partition Key (e.g., `NOTE#user123`)
- `GSI1SK`: Sort Key (e.g., `2025-01-15#note456`)

**Entity Types:**
1. **Notes**
   - PK: `USER#{userId}`
   - SK: `NOTE#{noteId}`
   - GSI1PK: `NOTE#{userId}`
   - GSI1SK: `{date}#{noteId}`

2. **Strategies**
   - PK: `USER#{userId}`
   - SK: `STRAT#{strategyId}`
   - GSI1PK: `STRAT#{userId}`
   - GSI1SK: `{timestamp}#{strategyId}`

## Technology Stack

### Backend
- **Runtime**: Python 3.11
- **Framework**: AWS Lambda (serverless)
- **Database**: DynamoDB (NoSQL)
- **Authentication**: AWS Cognito
- **API**: REST API via API Gateway

### Frontend
- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI
- **State Management**: React Hooks

### Infrastructure
- **IaC**: AWS CDK (TypeScript)
- **Containerization**: Docker
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana

## Design Patterns

### 1. Layered Architecture
- **Separation of Concerns**: Each layer has a specific responsibility
- **Dependency Direction**: API → Services → Repositories → Database
- **Testability**: Easy to mock dependencies

### 2. Repository Pattern
- **Abstraction**: Repository abstracts data access
- **Flexibility**: Can swap DynamoDB for another database
- **Testability**: Easy to mock repository for unit tests

### 3. Service Layer Pattern
- **Business Logic**: Encapsulates business rules
- **Reusability**: Services can be used by multiple controllers
- **Testability**: Business logic tested independently

### 4. Single Responsibility Principle
- Each module has one clear purpose
- Controllers handle HTTP, Services handle business logic, Repositories handle data

## Security

1. **Authentication**: AWS Cognito JWT tokens
2. **Authorization**: User-scoped data access
3. **CORS**: Configured for specific origins
4. **Input Validation**: Field filtering in repositories
5. **Secrets**: Environment variables, no hardcoded credentials

## Scalability Considerations

1. **Serverless**: Auto-scales with Lambda
2. **DynamoDB**: On-demand scaling
3. **CDN**: Frontend can be deployed to CloudFront
4. **Caching**: Can add API Gateway caching
5. **Database**: GSI for efficient queries

## Monitoring & Observability

1. **Health Checks**: `/v1/health` endpoint
2. **Metrics**: `/v1/metrics` (Prometheus format)
3. **Logging**: CloudWatch Logs
4. **Tracing**: Can add X-Ray for distributed tracing

## Deployment Architecture

```
GitHub Repository
       │
       ▼
┌──────────────┐
│ GitHub Actions│
│  CI/CD Pipeline│
└──────┬───────┘
       │
       ├──▶ Test & Build
       │
       ├──▶ Build Docker Images
       │
       └──▶ Deploy to AWS
              │
              ▼
       ┌──────────────┐
       │  AWS CDK     │
       │  Deployment  │
       └──────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │  AWS Resources  │
    │  - Lambda       │
    │  - API Gateway  │
    │  - DynamoDB     │
    │  - Cognito      │
    └─────────────────┘
```

## Future Enhancements

1. **Caching Layer**: Redis for frequently accessed data
2. **Message Queue**: SQS for async processing
3. **Search**: Elasticsearch for full-text search
4. **Analytics**: Data warehouse for reporting
5. **Multi-tenancy**: Support for organizations/teams

