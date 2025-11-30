.PHONY: help install start stop restart clean verify check-prerequisites setup-env deploy terraform-init terraform-plan terraform-apply terraform-destroy terraform-output

# Default target
help:
	@echo "MyTraderPal - Quick Start Commands"
	@echo ""
	@echo "Local Development:"
	@echo "  make install    - Install dependencies and setup environment"
	@echo "  make start      - Start frontend and backend containers"
	@echo "  make stop       - Stop all containers"
	@echo "  make restart    - Restart all containers"
	@echo "  make clean      - Stop containers and remove volumes"
	@echo "  make verify     - Verify services are running"
	@echo "  make logs       - View container logs"
	@echo ""
	@echo "Infrastructure (Terraform):"
	@echo "  make deploy           - Deploy infrastructure to AWS"
	@echo "  make terraform-init   - Initialize Terraform"
	@echo "  make terraform-plan   - Plan infrastructure changes"
	@echo "  make terraform-apply  - Apply infrastructure changes"
	@echo "  make terraform-destroy - Destroy infrastructure"
	@echo "  make terraform-output - Show Terraform outputs"
	@echo ""

# Detect Docker Compose command (v1 or v2)
DOCKER_COMPOSE := $(shell command -v docker-compose 2>/dev/null || echo "docker compose")

# Check prerequisites before installation
check-prerequisites:
	@echo "🔍 Checking prerequisites..."
	@command -v docker >/dev/null 2>&1 || { echo "❌ Error: Docker is not installed. Please install Docker Desktop."; exit 1; }
	@docker info >/dev/null 2>&1 || { echo "❌ Error: Docker is not running. Please start Docker Desktop."; exit 1; }
	@if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then \
		echo "❌ Error: Docker Compose is not installed."; \
		exit 1; \
	fi
	@echo "✅ Prerequisites check passed"

# Setup environment file from template
setup-env:
	@echo "📝 Setting up environment files..."
	@# Backend .env file
	@if [ ! -f src/app/.env ]; then \
		if [ -f src/app/.env.example ]; then \
			cp src/app/.env.example src/app/.env; \
			echo "✅ Created src/app/.env from template (backend)"; \
		else \
			echo "⚠️  Warning: .env.example not found, creating minimal .env"; \
			echo "TABLE_NAME=mtp_app" > src/app/.env; \
			echo "DEV_MODE=true" >> src/app/.env; \
			echo "AWS_REGION=us-east-1" >> src/app/.env; \
		fi; \
	else \
		echo "✅ src/app/.env already exists (backend)"; \
	fi
	@# Frontend .env file
	@if [ ! -f src/frontend-react/.env ]; then \
		if [ -f src/frontend-react/.env.example ]; then \
			cp src/frontend-react/.env.example src/frontend-react/.env; \
			echo "✅ Created src/frontend-react/.env from template"; \
		else \
			echo "⚠️  Warning: .env.example not found, creating minimal .env"; \
			echo "VITE_API_URL=http://localhost:9000" > src/frontend-react/.env; \
			echo "VITE_USER_POOL_ID=" >> src/frontend-react/.env; \
			echo "VITE_USER_POOL_CLIENT_ID=" >> src/frontend-react/.env; \
			echo "VITE_AWS_REGION=us-east-1" >> src/frontend-react/.env; \
		fi; \
	else \
		echo "✅ src/frontend-react/.env already exists"; \
	fi

# Setup Python virtual environment
setup-python:
	@echo "🐍 Setting up Python virtual environment..."
	@if [ ! -d .venv ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv .venv; \
		echo "✅ Virtual environment created"; \
	else \
		echo "✅ Virtual environment already exists"; \
	fi
	@echo "Installing Python dependencies..."
	@.venv/bin/pip install --quiet --upgrade pip > /dev/null 2>&1 || true
	@.venv/bin/pip install --quiet -r requirements.txt > /dev/null 2>&1 || .venv/bin/pip install -r requirements.txt
	@.venv/bin/pip install --quiet -r requirements-dev.txt > /dev/null 2>&1 || .venv/bin/pip install -r requirements-dev.txt
	@echo "✅ Python dependencies installed"

# Setup Frontend dependencies
setup-frontend:
	@echo "📦 Setting up Frontend dependencies..."
	@if [ ! -f src/frontend-react/package-lock.json ]; then \
		echo "⚠️  Warning: package-lock.json not found. This may cause issues."; \
	fi
	@if [ ! -d src/frontend-react/node_modules ]; then \
		echo "Installing npm dependencies..."; \
		cd src/frontend-react && \
		if [ -f package-lock.json ]; then \
			npm ci || npm install; \
		else \
			npm install; \
		fi && \
		cd ../..; \
		echo "✅ Frontend dependencies installed"; \
	else \
		echo "✅ Frontend dependencies already installed"; \
	fi

# Check optional tools (for infrastructure/deployment)
check-optional-tools:
	@echo "🔧 Checking optional tools..."
	@if ! command -v terraform >/dev/null 2>&1; then \
		echo "⚠️  Terraform not found (optional, needed for AWS deployment)"; \
		echo "   Install: brew install terraform  # macOS"; \
		echo "   Or: https://www.terraform.io/downloads"; \
	else \
		TERRAFORM_VERSION=$$(terraform version -json 2>/dev/null | grep -o '"terraform_version":"[^"]*"' | cut -d'"' -f4 || terraform version | head -1); \
		echo "✅ Terraform found: $$TERRAFORM_VERSION"; \
	fi
	@if ! command -v aws >/dev/null 2>&1; then \
		echo "⚠️  AWS CLI not found (optional, needed for AWS deployment)"; \
		echo "   Install: brew install awscli  # macOS"; \
		echo "   Or: https://aws.amazon.com/cli/"; \
		echo "   Then configure: aws configure"; \
	else \
		AWS_VERSION=$$(aws --version 2>/dev/null | cut -d' ' -f1); \
		echo "✅ AWS CLI found: $$AWS_VERSION"; \
		if ! aws sts get-caller-identity >/dev/null 2>&1; then \
			echo "⚠️  AWS CLI not configured. Run: aws configure"; \
		else \
			echo "✅ AWS CLI configured"; \
		fi; \
	fi
	@echo ""

# Install dependencies and setup
install: check-prerequisites setup-env setup-python setup-frontend check-optional-tools
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "🚀 MyTraderPal Installation Complete!"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "✅ Prerequisites verified:"
	@echo "   • Docker Desktop (running)"
	@echo "   • Make"
	@echo ""
	@echo "✅ Environment configured:"
	@echo "   • src/app/.env (backend environment variables)"
	@echo "   • src/frontend-react/.env (frontend environment variables)"
	@echo ""
	@echo "✅ Backend dependencies installed:"
	@echo "   • Python virtual environment (.venv)"
	@echo "   • Production dependencies (requirements.txt)"
	@echo "   • Development dependencies (requirements-dev.txt)"
	@echo ""
	@echo "✅ Frontend dependencies installed:"
	@echo "   • Node.js packages (node_modules)"
	@echo "   • All npm dependencies from package.json"
	@echo ""
	@echo "📦 Docker dependencies:"
	@echo "   • Will be installed automatically when containers start"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "💡 Quick Start Commands:"
	@echo ""
	@echo "   make start      - Start the application (frontend + backend)"
	@echo "   make test      - Run all tests with coverage"
	@echo "   make test-fast - Run tests without coverage (faster)"
	@echo "   make verify    - Verify services are running"
	@echo "   make logs      - View container logs"
	@echo ""
	@echo "💡 Manual Python Usage:"
	@echo ""
	@echo "   source .venv/bin/activate  # Activate virtual environment"
	@echo "   python -m pytest tests/    # Run tests manually"
	@echo "   deactivate                  # Deactivate when done"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "🎯 Next Step: Run 'make start' to start the application"
	@echo ""

# Start containers
start: check-prerequisites
	@echo "🚀 Starting MyTraderPal..."
	@echo ""
	@if $(DOCKER_COMPOSE) up -d --build; then \
		echo ""; \
		echo "⏳ Waiting for services to be ready..."; \
		sleep 5; \
		echo ""; \
		echo "✅ Services started!"; \
		echo ""; \
		echo "📍 Access your application:"; \
		echo "   Frontend:  http://localhost:3000"; \
		echo "   Backend:   http://localhost:9000"; \
		echo "   Health:    http://localhost:9000/v1/health"; \
		echo ""; \
		echo "🔍 Monitoring:"; \
		echo "   Prometheus: http://localhost:9090"; \
		echo "   Grafana:    http://localhost:3001 (admin/admin)"; \
		echo ""; \
		echo "💡 Useful commands:"; \
		echo "   make logs    - View logs"; \
		echo "   make stop    - Stop containers"; \
		echo "   make verify  - Verify services"; \
		echo ""; \
	else \
		echo ""; \
		echo "❌ Failed to start containers"; \
		echo "   Check if ports 3000 or 9000 are already in use"; \
		echo "   Run 'make logs' to see error details"; \
		exit 1; \
	fi

# Stop containers
stop:
	@echo "🛑 Stopping containers..."
	@$(DOCKER_COMPOSE) down 2>/dev/null || true
	@echo "✅ Containers stopped"

# Restart containers
restart: stop start

# Clean up (stop and remove volumes)
clean: stop
	@echo "🧹 Cleaning up..."
	@$(DOCKER_COMPOSE) down -v 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Verify services are running
verify: check-prerequisites
	@echo "🔍 Verifying services..."
	@echo ""
	@if $(DOCKER_COMPOSE) ps 2>/dev/null | grep -q "Up"; then \
		echo "✅ Containers are running"; \
		echo ""; \
		echo "Testing endpoints..."; \
		sleep 2; \
		if curl -s http://localhost:9000/v1/health >/dev/null 2>&1; then \
			echo "✅ Backend health check passed"; \
		else \
			echo "⚠️  Backend health check failed (may still be starting)"; \
		fi; \
		if curl -s http://localhost:3000 >/dev/null 2>&1; then \
			echo "✅ Frontend is accessible"; \
		else \
			echo "⚠️  Frontend check failed (may still be starting)"; \
		fi; \
		if curl -s http://localhost:9090/-/healthy >/dev/null 2>&1; then \
			echo "✅ Prometheus is accessible"; \
		else \
			echo "⚠️  Prometheus check failed (may still be starting)"; \
		fi; \
		if curl -s http://localhost:3001/api/health >/dev/null 2>&1; then \
			echo "✅ Grafana is accessible"; \
		else \
			echo "⚠️  Grafana check failed (may still be starting)"; \
		fi; \
		echo ""; \
		echo "📍 URLs:"; \
		echo "   Frontend:  http://localhost:3000"; \
		echo "   Backend:   http://localhost:9000"; \
		echo "   Prometheus: http://localhost:9090"; \
		echo "   Grafana:    http://localhost:3001"; \
	else \
		echo "❌ Containers are not running"; \
		echo "   Run 'make start' to start them"; \
		exit 1; \
	fi

# View logs
logs:
	@$(DOCKER_COMPOSE) logs -f

# Quick status check
status:
	@$(DOCKER_COMPOSE) ps

# ============================================================================
# Testing Commands (using virtual environment)
# ============================================================================

# Run tests with coverage
test:
	@echo "🧪 Running tests..."
	@if [ ! -d .venv ]; then \
		echo "❌ Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	@.venv/bin/python -m pytest tests/ \
		--cov=src/app \
		--cov-report=term-missing \
		--cov-report=html \
		--cov-fail-under=70 \
		-v

# Run tests without coverage
test-fast:
	@echo "🧪 Running tests (fast mode)..."
	@if [ ! -d .venv ]; then \
		echo "❌ Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	@.venv/bin/python -m pytest tests/ -v

# View coverage report
coverage:
	@echo "📊 Opening coverage report..."
	@if [ ! -f htmlcov/index.html ]; then \
		echo "❌ Coverage report not found. Run 'make test' first."; \
		exit 1; \
	fi
	@open htmlcov/index.html 2>/dev/null || xdg-open htmlcov/index.html 2>/dev/null || echo "Open htmlcov/index.html in your browser"

# ============================================================================
# Terraform Infrastructure Commands
# ============================================================================

TERRAFORM_DIR := infra/terraform

# Check Terraform prerequisites
check-terraform:
	@command -v terraform >/dev/null 2>&1 || { echo "❌ Error: Terraform is not installed. Install from https://www.terraform.io/downloads"; exit 1; }
	@aws sts get-caller-identity >/dev/null 2>&1 || { echo "❌ Error: AWS CLI is not configured. Run: aws configure"; exit 1; }

# Initialize Terraform
terraform-init: check-terraform
	@echo "📦 Initializing Terraform..."
	@cd $(TERRAFORM_DIR) && terraform init

# Plan infrastructure changes
terraform-plan: check-terraform
	@echo "📋 Planning infrastructure changes..."
	@cd $(TERRAFORM_DIR) && terraform plan

# Apply infrastructure changes
terraform-apply: check-terraform
	@echo "🚀 Applying infrastructure changes..."
	@cd $(TERRAFORM_DIR) && terraform apply

# Destroy infrastructure
terraform-destroy: check-terraform
	@echo "⚠️  WARNING: This will destroy all infrastructure!"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm && [ "$$confirm" = "yes" ] || exit 1
	@cd $(TERRAFORM_DIR) && terraform destroy

# Show Terraform outputs
terraform-output: check-terraform
	@cd $(TERRAFORM_DIR) && terraform output

# Deploy infrastructure (full workflow)
deploy: check-terraform
	@echo "🚀 Deploying MyTraderPal infrastructure..."
	@echo ""
	@cd $(TERRAFORM_DIR) && \
		if [ ! -f terraform.tfvars ]; then \
			echo "⚠️  terraform.tfvars not found, copying from example..."; \
			cp terraform.tfvars.example terraform.tfvars; \
			echo "   Please edit terraform.tfvars before deploying"; \
			echo ""; \
			read -p "Press Enter to continue or Ctrl+C to cancel..."; \
		fi && \
		terraform init && \
		terraform plan && \
		echo "" && \
		read -p "Apply these changes? (yes/no): " confirm && \
		[ "$$confirm" = "yes" ] && \
		terraform apply -auto-approve && \
		echo "" && \
		echo "✅ Deployment complete!" && \
		echo "" && \
		terraform output

