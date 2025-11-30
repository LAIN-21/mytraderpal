# Getting Started - Complete Development Process

This guide walks you through the entire development process from scratch.

## 🚀 Quick Start (First Time Setup)

### Prerequisites

Before you begin, ensure you have:

1. **Docker Desktop** installed and running
   - Download: https://www.docker.com/products/docker-desktop
   - Verify: `docker --version` and `docker info`

2. **Git** installed
   - Verify: `git --version`

3. **Make** (usually pre-installed on Mac/Linux)
   - Verify: `make --version`

4. **AWS CLI** (optional, only for deployment)
   - Install: https://aws.amazon.com/cli/
   - Configure: `aws configure`

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd mytraderpal
```

### Step 2: Install and Setup

```bash
make install
```

**What this does:**
- ✅ Checks prerequisites (Docker, etc.)
- ✅ Creates `.env` files from templates:
  - `src/app/.env` (backend configuration)
  - `src/frontend-react/.env` (frontend configuration)
- ✅ Sets up default values for local development

### Step 3: Start Development Environment

```bash
make start
```

**What this does:**
- ✅ Builds Docker images for backend and frontend
- ✅ Starts containers with hot reloading enabled
- ✅ Mounts source code as volumes (changes immediately visible)
- ✅ Sets up networking between services

**Services available:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:9000
- **Health Check**: http://localhost:9000/v1/health

### Step 4: Verify Everything Works

```bash
make verify
```

This checks:
- ✅ Containers are running
- ✅ Backend health endpoint responds
- ✅ Frontend is accessible

---

## 💻 Daily Development Workflow

### Starting Your Day

```bash
# Start containers (if not already running)
make start

# Or if containers are stopped
make restart
```

### Making Changes

1. **Edit Code**
   - Backend: Edit files in `src/app/`
   - Frontend: Edit files in `src/frontend-react/src/`

2. **Changes Are Automatic**
   - **Backend**: Lambda RIE reloads code on each request
   - **Frontend**: Vite HMR automatically refreshes browser
   - **No rebuild needed** - just save and test!

3. **Test Your Changes**
   - Open browser: http://localhost:3000
   - Check backend: http://localhost:9000/v1/health
   - View logs: `make logs`

### Viewing Logs

```bash
# View all container logs
make logs

# Or view specific service
docker-compose logs api      # Backend logs
docker-compose logs frontend # Frontend logs

# Follow logs in real-time
docker-compose logs -f api
```

### Stopping Development

```bash
# Stop containers (keeps data)
make stop

# Stop and remove volumes (clean slate)
make clean
```

---

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/app --cov-report=html

# Run specific test file
pytest tests/test_notes.py

# Run with verbose output
pytest tests/ -v
```

### Frontend Tests

```bash
cd src/frontend-react

# Run tests
npm test

# Run linter
npm run lint

# Build (to verify it works)
npm run build
```

### Integration Testing

Test the full stack locally:

```bash
# Start services
make start

# Test backend API
curl http://localhost:9000/v1/health

# Test with authentication (dev mode)
curl -H "X-MTP-Dev-User: test-user" http://localhost:9000/v1/notes

# Open frontend in browser
open http://localhost:3000
```

---

## 📁 Project Structure

```
mytraderpal/
├── src/
│   ├── app/                    # Backend (Python Lambda)
│   │   ├── api/                # API handlers
│   │   ├── core/               # Core utilities (auth, response, etc.)
│   │   ├── repositories/       # Data access layer
│   │   ├── services/           # Business logic
│   │   ├── main.py             # Lambda handler entry point
│   │   └── .env                # Backend environment variables
│   │
│   └── frontend-react/          # Frontend (React + Vite)
│       ├── src/
│       │   ├── components/     # React components
│       │   ├── pages/          # Page components
│       │   ├── lib/            # Utilities (API client, auth, etc.)
│       │   └── main.tsx        # App entry point
│       └── .env                 # Frontend environment variables
│
├── tests/                       # Backend tests
├── infra/
│   ├── docker/                 # Dockerfiles
│   │   ├── Dockerfile          # Dev Dockerfile (with proxy)
│   │   └── Dockerfile.prod     # Production Dockerfile
│   └── terraform/              # Infrastructure as code
│       ├── modules/            # Terraform modules
│       └── main.tf             # Main Terraform config
│
├── docker-compose.yml          # Local development setup
├── Makefile                    # Development commands
└── requirements.txt            # Python dependencies
```

---

## 🔧 Configuration

### Backend Environment Variables (`src/app/.env`)

```env
# DynamoDB Configuration
TABLE_NAME=mtp_app

# Development Mode
# Set to "true" to bypass Cognito authentication
DEV_MODE=true

# AWS Configuration
AWS_REGION=us-east-1

# AWS Credentials (optional, uses ~/.aws/credentials if available)
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
```

### Frontend Environment Variables (`src/frontend-react/.env`)

```env
# API Configuration
VITE_API_URL=http://localhost:9000

# AWS Cognito Configuration (optional for local dev)
VITE_USER_POOL_ID=
VITE_USER_POOL_CLIENT_ID=
VITE_AWS_REGION=us-east-1
```

**Note:** For local development, you can leave Cognito credentials empty. The app will use `X-MTP-Dev-User` header when `DEV_MODE=true`.

---

## 🐛 Troubleshooting

### Containers Won't Start

```bash
# Check if ports are in use
lsof -i :3000  # Frontend port
lsof -i :9000  # Backend port

# Restart Docker Desktop
# Then try again
make restart
```

### Changes Not Reflecting

```bash
# Restart containers
make restart

# Check if volumes are mounted correctly
docker-compose ps
docker-compose exec api ls -la /var/task/app
```

### Backend Not Responding

```bash
# Check backend logs
docker-compose logs api

# Test backend directly
curl http://localhost:9000/v1/health

# Check if Lambda RIE is running
docker-compose exec api ps aux
```

### Frontend Not Loading

```bash
# Check frontend logs
docker-compose logs frontend

# Verify Vite is running
curl http://localhost:3000

# Check if node_modules are installed
docker-compose exec frontend ls -la /app/node_modules
```

### Environment Variables Not Working

```bash
# Verify .env files exist
ls -la src/app/.env
ls -la src/frontend-react/.env

# Check if variables are loaded
docker-compose exec api env | grep TABLE_NAME
docker-compose exec frontend env | grep VITE_API_URL
```

---

## 🚀 Deployment Process

### Automatic Deployment (CI/CD)

When you push to `main` branch:

1. **GitHub Actions runs:**
   - ✅ Backend tests (pytest)
   - ✅ Frontend tests (npm test)
   - ✅ Builds Docker images
   - ✅ Pushes images to ECR
   - ✅ Deploys with Terraform

### Manual Deployment

```bash
# Deploy infrastructure
make deploy

# Or step by step
make terraform-init
make terraform-plan
make terraform-apply
```

### Deployment Checklist

Before deploying:

- [ ] All tests pass locally
- [ ] Code is committed and pushed
- [ ] Environment variables are set in GitHub Secrets
- [ ] Terraform variables are configured (`terraform.tfvars`)

---

## 📚 Common Tasks

### Adding a New API Endpoint

1. **Create handler** in `src/app/api/`
   ```python
   # src/app/api/new_feature.py
   def get_new_feature(event, user_id):
       # Your code here
       return success_response({"data": "..."})
   ```

2. **Add route** in `src/app/api/router.py`
   ```python
   elif path == '/v1/new-feature' and http_method == 'GET':
       response = new_feature.get_new_feature(event, user_id)
   ```

3. **Test locally**
   ```bash
   curl http://localhost:9000/v1/new-feature
   ```

4. **No rebuild needed** - changes are live immediately!

### Adding a New Frontend Page

1. **Create page** in `src/frontend-react/src/pages/`
   ```typescript
   // NewPage.tsx
   export default function NewPage() {
     return <div>New Page</div>
   }
   ```

2. **Add route** in `src/frontend-react/src/App.tsx`
   ```typescript
   <Route path="/new-page" element={<NewPage />} />
   ```

3. **Test locally** - Vite HMR will reload automatically!

### Adding a New Dependency

**Backend:**
```bash
# Add to requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# Restart containers to install
make restart
```

**Frontend:**
```bash
cd src/frontend-react
npm install new-package
# Changes are picked up automatically
```

---

## 🎯 Development Best Practices

### Code Organization

- **Backend**: Follow the existing structure (api/, core/, repositories/, services/)
- **Frontend**: Use components/ for reusable UI, pages/ for routes
- **Tests**: Keep tests close to code they test

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push and create PR
git push origin feature/new-feature
```

### Testing

- ✅ Write tests for new features
- ✅ Run tests before committing
- ✅ Aim for 70%+ code coverage (enforced in CI)

### Code Quality

- ✅ Run linters before committing
- ✅ Follow existing code style
- ✅ Remove console.logs before committing
- ✅ Add comments for complex logic

---

## 📖 Additional Resources

- **Architecture**: See `docs/ARCHITECTURE.md`
- **Deployment Details**: See `docs/DEVELOPMENT_TO_DEPLOYMENT.md`
- **API Documentation**: See `docs/API.md` (if available)
- **Terraform**: See `infra/terraform/README.md`

---

## 🆘 Getting Help

If you encounter issues:

1. **Check logs**: `make logs`
2. **Verify setup**: `make verify`
3. **Check documentation**: `docs/` directory
4. **Review error messages**: They usually point to the issue

---

## ✅ Quick Reference

```bash
# Setup (first time)
make install

# Start development
make start

# Stop development
make stop

# Restart services
make restart

# View logs
make logs

# Run tests
pytest tests/
cd src/frontend-react && npm test

# Verify everything works
make verify

# Clean up
make clean

# Deploy
make deploy
```

---

**Happy coding! 🎉**

