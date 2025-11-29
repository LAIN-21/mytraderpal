# Development Guide

## Quick Start

### Option 1: Frontend Only (Recommended for UI Development)

```bash
# 1. Install frontend dependencies
cd src/frontend
npm install

# 2. Set up environment variables
cp env.example .env.local
# Edit .env.local with your API URL (point to deployed API or local backend)

# 3. Run frontend
npm run dev
```

Visit `http://localhost:3000`

### Option 2: Full Stack with Docker

```bash
# 1. Build and run with docker-compose
docker-compose up --build

# Backend: http://localhost:9000
# Frontend: http://localhost:3000
```

### Option 3: Backend Testing (Lambda Local)

Since the backend is a Lambda function, you can test it locally using:

```bash
# 1. Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 2. Use dev mode header for testing
# See "Testing API Locally" section below
```

## Detailed Setup

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker** (optional, for containerized development)
- **AWS CLI** (optional, for deployment)

### Backend Development

#### 1. Setup Python Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### 2. Environment Variables

Create a `.env` file in the root:

```bash
TABLE_NAME=mtp_app
DEV_MODE=true
AWS_REGION=us-east-1
```

#### 3. Testing Backend Locally

The backend is a Lambda function, so you can't run it as a traditional server. Instead:

**Option A: Use AWS SAM Local**
```bash
# Install SAM CLI
brew install aws-sam-cli  # macOS
# or
pip install aws-sam-cli

# Run locally
sam local start-api --template template.yaml
```

**Option B: Test with Python Script**
Create a test script to invoke the handler:

```python
# test_local.py
import json
from src.app.main import handler

event = {
    'httpMethod': 'GET',
    'path': '/v1/health',
    'headers': {'X-MTP-Dev-User': 'test-user'},
    'queryStringParameters': {}
}

result = handler(event, None)
print(json.dumps(json.loads(result['body']), indent=2))
```

Run: `python test_local.py`

**Option C: Use Docker Lambda Runtime**
```bash
docker run -p 9000:8080 \
  -v $(pwd)/src/app:/var/task \
  -e TABLE_NAME=mtp_app \
  -e DEV_MODE=true \
  public.ecr.aws/lambda/python:3.11 \
  main.handler
```

### Frontend Development

#### 1. Setup

```bash
cd src/frontend
npm install
```

#### 2. Environment Variables

Create `src/frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:9000
NEXT_PUBLIC_USER_POOL_ID=your-pool-id
NEXT_PUBLIC_USER_POOL_CLIENT_ID=your-client-id
NEXT_PUBLIC_AWS_REGION=us-east-1
```

#### 3. Run Development Server

```bash
npm run dev
```

Visit `http://localhost:3000`

#### 4. Development Features

- Hot reload on file changes
- TypeScript type checking
- ESLint warnings in console
- Fast Refresh for React components

## Testing API Locally

### Using curl with Dev Mode

```bash
# Health check
curl http://localhost:9000/v1/health

# Create note (with dev user header)
curl -X POST http://localhost:9000/v1/notes \
  -H "X-MTP-Dev-User: test-user-123" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test note", "date": "2025-01-15"}'

# List notes
curl http://localhost:9000/v1/notes \
  -H "X-MTP-Dev-User: test-user-123"
```

### Using Python Requests

```python
import requests

headers = {'X-MTP-Dev-User': 'test-user-123'}
response = requests.get('http://localhost:9000/v1/health', headers=headers)
print(response.json())
```

## Running Tests

```bash
# Run all tests
./scripts/test.sh

# Or manually
python -m pytest tests/unit/ \
  --cov=src/app \
  --cov-report=term-missing \
  --cov-fail-under=70 \
  -v
```

## Development Workflow

### 1. Make Code Changes

- Backend: Edit files in `src/app/`
- Frontend: Edit files in `src/frontend/`

### 2. Test Changes

- Backend: Run `./scripts/test.sh`
- Frontend: Check browser console and terminal

### 3. Lint Code

```bash
./scripts/lint.sh
```

### 4. Run Locally

```bash
# Option 1: Docker
docker-compose up

# Option 2: Frontend only (if using deployed backend)
cd src/frontend && npm run dev
```

## Common Development Tasks

### Adding a New API Endpoint

1. Add route handler in `src/app/api/`
2. Add service method in `src/app/services/`
3. Update router in `src/app/api/router.py`
4. Add tests in `tests/unit/`

### Adding a New Frontend Page

1. Create page in `src/frontend/app/`
2. Add route in Next.js app router
3. Update navigation if needed

### Debugging

**Backend:**
- Add `print()` statements (will show in Lambda logs)
- Use `pytest -v` for detailed test output
- Check CloudWatch logs when deployed

**Frontend:**
- Use browser DevTools
- Check Next.js terminal output
- Use React DevTools extension

## Troubleshooting

### Backend Issues

**Import Errors:**
```bash
# Ensure src/ is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

**DynamoDB Connection:**
- For local dev, use `DEV_MODE=true` to bypass real DynamoDB
- Tests use mocks, no real AWS needed

### Frontend Issues

**API Connection Errors:**
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Ensure backend is running
- Check CORS settings

**Build Errors:**
```bash
# Clear Next.js cache
rm -rf src/frontend/.next
npm run build
```

## Recommended Development Setup

1. **Terminal 1**: Frontend dev server
   ```bash
   cd src/frontend && npm run dev
   ```

2. **Terminal 2**: Backend testing
   ```bash
   source .venv/bin/activate
   pytest tests/unit/ -v --watch  # if using pytest-watch
   ```

3. **Terminal 3**: Docker services (if using)
   ```bash
   docker-compose up
   ```

## Next Steps

- See [README.md](README.md) for deployment
- See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for architecture details
- See [docs/SDLC.md](docs/SDLC.md) for development process

