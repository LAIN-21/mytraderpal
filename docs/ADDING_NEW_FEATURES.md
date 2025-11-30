# Adding New Features - How It Works

## 🏗️ Architecture Overview

**Important:** You have **ONE Lambda function** that handles **ALL API routes**. This is a **monolith pattern**, not microservices.

```
API Gateway
    ↓
Single Lambda Function (mytraderpal-api)
    ↓
Router (router.py) - Routes requests to handlers
    ↓
├─→ notes.py (handles /v1/notes/*)
├─→ strategies.py (handles /v1/strategies/*)
├─→ reports.py (handles /v1/reports/*)
└─→ [Your new feature] (handles /v1/new-feature/*)
```

## ❌ Common Misconception

**You do NOT create a new Lambda function for each feature.**

Instead:
- ✅ Add new handlers/routes to the **existing** Lambda function
- ✅ All code lives in `src/app/`
- ✅ Infrastructure (Terraform) manages **one** Lambda function
- ✅ When you deploy, the **entire** Lambda function is updated

## ✅ How to Add a New Feature

### Example: Adding a "Portfolio" Feature

#### Step 1: Create Handler (`src/app/api/portfolio.py`)

```python
"""Portfolio API handlers."""
from typing import Dict, Any
from app.core.response import success_response, error_response, get_origin

def get_portfolio(event: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Get user's portfolio."""
    try:
        # Your business logic here
        portfolio_data = {
            "user_id": user_id,
            "holdings": [],
            "total_value": 0
        }
        return success_response(portfolio_data, get_origin(event))
    except Exception as e:
        return error_response(500, f'Failed to get portfolio: {str(e)}', get_origin(event))

def create_holding(event: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Create a new holding."""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        # Your business logic here
        return success_response({"id": "holding-123"}, get_origin(event), 201)
    except Exception as e:
        return error_response(400, f'Failed to create holding: {str(e)}', get_origin(event))
```

#### Step 2: Add Routes (`src/app/api/router.py`)

```python
# Add import at top
from app.api import notes, strategies, reports, metrics, portfolio  # Add portfolio

# Add routes in route_request() function
# Portfolio routes
elif path == '/v1/portfolio' and http_method == 'GET':
    response = portfolio.get_portfolio(event, user_id)
elif path == '/v1/portfolio' and http_method == 'POST':
    response = portfolio.create_holding(event, user_id)
elif path.startswith('/v1/portfolio/') and http_method == 'GET':
    base_path, holding_id = extract_path_params(path)
    if not holding_id:
        response = error_response(400, 'Holding ID required', origin)
    else:
        response = portfolio.get_holding(event, user_id, holding_id)
```

#### Step 3: Test Locally

```bash
# Start development environment
make start

# Test new endpoint
curl http://localhost:9000/v1/portfolio

# With authentication (dev mode)
curl -H "X-MTP-Dev-User: test-user" http://localhost:9000/v1/portfolio
```

**No rebuild needed!** Changes are immediately available.

#### Step 4: Deploy to AWS

**Infrastructure does NOT automatically detect changes.** You need to deploy:

```bash
# Option 1: Automatic (via CI/CD)
git add .
git commit -m "Add portfolio feature"
git push origin main
# GitHub Actions will deploy automatically

# Option 2: Manual
make deploy
```

**What happens during deployment:**
1. Docker image is built with your new code
2. Image is pushed to ECR
3. Terraform updates the **same Lambda function** with new image
4. Lambda function now includes your new routes

## 📁 File Structure for New Features

```
src/app/
├── api/
│   ├── router.py          # Add routes here
│   ├── portfolio.py       # New feature handler (you create this)
│   ├── notes.py
│   └── strategies.py
├── services/
│   └── portfolio_service.py  # Business logic (optional)
├── repositories/
│   └── portfolio_repository.py  # Data access (optional)
└── main.py                # Entry point (no changes needed)
```

## 🔄 Deployment Process

### What Gets Updated

When you deploy:
- ✅ **One Lambda function** is updated
- ✅ The entire `src/app/` directory is packaged into Docker image
- ✅ All routes (old + new) are included
- ✅ No new Lambda functions are created

### Infrastructure Changes

**Terraform does NOT need changes** for new features:
- ✅ Same Lambda function resource
- ✅ Same API Gateway (routes are handled in code)
- ✅ No new infrastructure needed

**Only update Terraform if:**
- ❌ You need a **separate** Lambda function (rare)
- ❌ You need new AWS resources (DynamoDB table, S3 bucket, etc.)
- ❌ You need new IAM permissions

## 🎯 Complete Example: Adding "Analytics" Feature

### 1. Create Handler

```python
# src/app/api/analytics.py
from typing import Dict, Any
from app.core.response import success_response, error_response, get_origin
import json

def get_analytics(event: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Get user analytics."""
    try:
        # Your logic here
        analytics = {
            "user_id": user_id,
            "total_trades": 100,
            "win_rate": 0.65
        }
        return success_response(analytics, get_origin(event))
    except Exception as e:
        return error_response(500, str(e), get_origin(event))
```

### 2. Update Router

```python
# src/app/api/router.py

# Add import
from app.api import notes, strategies, reports, metrics, analytics

# Add route
elif path == '/v1/analytics' and http_method == 'GET':
    response = analytics.get_analytics(event, user_id)
```

### 3. Test Locally

```bash
make start
curl -H "X-MTP-Dev-User: test-user" http://localhost:9000/v1/analytics
```

### 4. Deploy

```bash
git add .
git commit -m "Add analytics endpoint"
git push origin main
```

**That's it!** The same Lambda function now handles `/v1/analytics`.

## ❓ FAQ

### Q: Do I need to update Terraform for new features?

**A:** No! Terraform manages infrastructure (Lambda function, API Gateway, DynamoDB, etc.). Adding new routes/handlers is just code changes.

### Q: Will this create a new Lambda function?

**A:** No. All features share the same Lambda function. The router directs requests to the right handler.

### Q: How does API Gateway know about new routes?

**A:** API Gateway is configured with a catch-all route (`/{proxy+}`) that forwards all requests to Lambda. The Lambda router handles routing in code.

### Q: What if I need a separate Lambda function?

**A:** That's a different architecture (microservices). You would:
1. Create new handler in `src/app/`
2. Create new Lambda function in Terraform
3. Update API Gateway to route to new function

But for most features, adding routes to the existing function is simpler.

### Q: How do I add a new DynamoDB table?

**A:** That requires Terraform changes:
1. Add table in `infra/terraform/modules/dynamodb/` or create new module
2. Update Lambda IAM permissions
3. Deploy with `make deploy`

## 📊 Summary

**For New Features:**
- ✅ Add code in `src/app/api/`
- ✅ Update `router.py` with new routes
- ✅ Test locally (hot reload)
- ✅ Deploy (updates same Lambda function)

**Infrastructure:**
- ✅ No Terraform changes needed for new routes
- ✅ Same Lambda function handles all routes
- ✅ Deployment updates entire function with new code

**Key Point:** Think of it as adding new endpoints to a single API, not creating new services.

