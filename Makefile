.PHONY: help install test test-cov lint format clean run

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  test        - Run tests"
	@echo "  test-cov    - Run tests with coverage report"
	@echo "  lint        - Run linting checks"
	@echo "  format      - Format code"
	@echo "  clean       - Clean up temporary files"
	@echo "  run         - Run the application"

# Install dependencies
install:
	uv sync --dev

# Run tests
test:
	uv run pytest tests/ -v

# Run tests with coverage
test-cov:
	uv run pytest tests/ -v --cov=main --cov-report=term-missing --cov-report=html

# Run linting
lint:
	uv run ruff check main.py tests/

# Format code
format:
	uv run ruff format main.py tests/

# Clean up temporary files
clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run the application
run:
	uv run main.py

# Run all checks (lint + test)
check: lint test

# Run everything (format + lint + test)
all: format lint test-cov