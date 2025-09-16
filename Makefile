.PHONY: help install install-dev test test-cov lint format clean run docker-build docker-up docker-down docker-logs

help: ## Show this help message
	@echo "Vanna AI Web Application - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=app --cov-report=html --cov-report=term-missing

lint: ## Run linting checks
	flake8 app/
	mypy app/

format: ## Format code
	black app/
	isort app/

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

run: ## Run the application
	python -m app.main

run-simple: ## Run with simple script
	python run.py

docker-build: ## Build Docker image
	docker build -t vanna-ai-webapp .

docker-up: ## Start Docker services
	docker-compose up -d

docker-down: ## Stop Docker services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f app

docker-restart: ## Restart Docker services
	docker-compose restart

demo: ## Run demo script
	python examples/demo.py

setup: install-dev ## Setup development environment
	@echo "Development environment setup complete!"
	@echo "Run 'make run' to start the application"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make demo' to run the demo script"

dev: format lint test ## Run all development checks
	@echo "All development checks passed!"
