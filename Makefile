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

# Install dependencies and setup
install: check-prerequisites setup-env
	@echo ""
	@echo "🚀 Installing MyTraderPal..."
	@echo ""
	@echo "✅ Prerequisites verified"
	@echo "✅ Environment files configured"
	@echo ""
	@echo "📦 Dependencies will be installed when containers start"
	@echo ""
	@echo "✅ Installation complete!"
	@echo ""
	@echo "Next step: Run 'make start' to start the application"

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
		echo "   Frontend: http://localhost:3000"; \
		echo "   Backend:  http://localhost:9000"; \
		echo "   Health:   http://localhost:9000/v1/health"; \
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
		echo ""; \
		echo "📍 URLs:"; \
		echo "   Frontend: http://localhost:3000"; \
		echo "   Backend:  http://localhost:9000"; \
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

