.PHONY: dev test test-unit test-integration lint format coverage clean

# Development
dev:
	@echo "Starting development server..."
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing
test: test-unit test-integration
	@echo "All tests passed!"

test-unit:
	@echo "Running unit tests..."
	uv run pytest tests/ -v -k "not integration"

test-integration:
	@echo "Running integration tests..."
	uv run pytest tests/ -v -k "integration"

test-all:
	@echo "Running all tests..."
	uv run pytest tests/ -v

coverage:
	@echo "Running tests with coverage..."
	uv run pytest tests/ -v --cov=app --cov-report=html --cov-report=term

coverage-html:
	@echo "Running tests with coverage and generating HTML report..."
	uv run pytest tests/ -v --cov=app --cov-report=html
	@echo "Coverage report generated at htmlcov/index.html"

# Linting and Formatting
lint:
	@echo "Running linter..."
	uv run ruff check app/ tests/

format:
	@echo "Formatting code..."
	uv run black app/ tests/
	uv run ruff check --fix app/ tests/

# Clean
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .coverage htmlcov 2>/dev/null || true
