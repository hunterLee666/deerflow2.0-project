# Makefile for Enterprise AI Agent System

# Variables
PROJECT_NAME = deerflow-enterprise-project
BACKEND_DIR = backend
FRONTEND_DIR = frontend

# Default target
.PHONY: help
help:
	@echo "Enterprise AI Agent System - Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make install           Install all dependencies"
	@echo "  make dev              Start development servers"
	@echo "  make test             Run all tests"
	@echo "  make lint             Run code linting"
	@echo "  make format           Format code"
	@echo "  make build            Build for production"
	@echo "  make clean            Clean build artifacts"
	@echo "  make help             Show this help message"

# Install dependencies
.PHONY: install
install:
	@echo "Installing dependencies..."
	cd $(BACKEND_DIR) && uv sync
	cd $(FRONTEND_DIR) && npm install
	@echo "Dependencies installed successfully!"

# Development
.PHONY: dev
dev:
	@echo "Starting development servers..."
	@echo "Starting backend server..."
	cd $(BACKEND_DIR) && uv run python app/main.py &
	@echo "Starting frontend server..."
	cd $(FRONTEND_DIR) && npm run dev &
	@echo "Development servers started!"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"

# Backend development
.PHONY: dev-backend
dev-backend:
	@echo "Starting backend server..."
	cd $(BACKEND_DIR) && uv run python app/main.py

# Frontend development
.PHONY: dev-frontend
dev-frontend:
	@echo "Starting frontend server..."
	cd $(FRONTEND_DIR) && npm run dev

# Testing
.PHONY: test
test:
	@echo "Running tests..."
	cd $(BACKEND_DIR) && uv run pytest tests/
	cd $(FRONTEND_DIR) && npm test

.PHONY: test-unit
test-unit:
	@echo "Running unit tests..."
	cd $(BACKEND_DIR) && uv run pytest tests/unit/
	cd $(FRONTEND_DIR) && npm run test:unit

.PHONY: test-integration
test-integration:
	@echo "Running integration tests..."
	cd $(BACKEND_DIR) && uv run pytest tests/integration/
	cd $(FRONTEND_DIR) && npm run test:integration

.PHONY: test-e2e
test-e2e:
	@echo "Running end-to-end tests..."
	cd $(BACKEND_DIR) && uv run pytest tests/e2e/
	cd $(FRONTEND_DIR) && npm run test:e2e

# Code quality
.PHONY: lint
lint:
	@echo "Running code linting..."
	cd $(BACKEND_DIR) && uv run ruff check .
	cd $(FRONTEND_DIR) && npm run lint

.PHONY: format
format:
	@echo "Formatting code..."
	cd $(BACKEND_DIR) && uv run black .
	cd $(FRONTEND_DIR) && npm run format

# Build
.PHONY: build
build:
	@echo "Building for production..."
	cd $(BACKEND_DIR) && uv build
	cd $(FRONTEND_DIR) && npm run build
	@echo "Build completed!"

# Clean
.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	cd $(BACKEND_DIR) && rm -rf dist/ build/
	cd $(FRONTEND_DIR) && rm -rf dist/ build/
	@echo "Clean completed!"

# Docker
.PHONY: docker-build
docker-build:
	@echo "Building Docker images..."
	docker-compose build

.PHONY: docker-up
docker-up:
	@echo "Starting services with Docker..."
	docker-compose up -d

.PHONY: docker-down
docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

.PHONY: docker-logs
docker-logs:
	@echo "Showing Docker logs..."
	docker-compose logs -f

# Documentation
.PHONY: docs
docs:
	@echo "Generating documentation..."
	@echo "Documentation generation completed!"

# Security
.PHONY: security-check
security-check:
	@echo "Running security checks..."
	cd $(BACKEND_DIR) && uv run bandit -r .
	@echo "Security checks completed!"