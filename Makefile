# 0RB_AETHER Makefile
# Usage: make [target]

.PHONY: help install run docker test clean

# Default target
help:
	@echo "0RB_AETHER - Available Commands"
	@echo ""
	@echo "  make install    Install dependencies"
	@echo "  make run        Run locally"
	@echo "  make docker     Run with Docker"
	@echo "  make test       Run tests"
	@echo "  make clean      Clean up"
	@echo ""

# Install dependencies
install:
	pip install -r requirements.txt

# Run locally
run:
	python launcher.py

# Run with Docker
docker:
	docker compose up -d
	@echo ""
	@echo "Services: http://localhost:8080"

# Run with Docker (with logs)
docker-logs:
	docker compose up

# Stop Docker
docker-stop:
	docker compose down

# Run tests
test:
	python -m pytest -v

# Run specific test module
test-%:
	python -m pytest -v $*

# Clean up
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
	rm -rf venv 2>/dev/null || true

# Build Docker image
build:
	docker build -t orb-aether .

# Quick demo
demo:
	@echo "Running demos..."
	python -c "from flowsync import demo; import asyncio; asyncio.run(demo())"
	python -c "from marketplace import demo; import asyncio; asyncio.run(demo())"

# Development mode
dev:
	python launcher.py --debug
