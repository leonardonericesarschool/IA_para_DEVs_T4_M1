.PHONY: help install dev test test-cov lint docker-build docker-up docker-down clean migrations migrate

help:
	@echo "Pix Key Management API - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install              Install dependencies"
	@echo "  make dev                  Setup development environment"
	@echo ""
	@echo "Development:"
	@echo "  make run                  Run API locally (requires poetry/venv)"
	@echo "  make test                 Run all tests"
	@echo "  make test-cov             Run tests with coverage report"
	@echo "  make lint                 Run linting checks"
	@echo ""
	@echo "Database:"
	@echo "  make migrations           Create new migration"
	@echo "  make migrate              Apply migrations"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build         Build Docker image"
	@echo "  make docker-up            Start services with docker-compose"
	@echo "  make docker-down          Stop services"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean                Remove __pycache__ and .pytest_cache"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt
	pip install pytest pytest-asyncio pytest-cov httpx

run:
	python src/main.py

test:
	pytest

test-cov:
	pytest --cov=src --cov-report=html --cov-report=term

lint:
	ruff check src tests || echo "ruff not installed, skipping"
	black --check src tests || echo "black not installed, skipping"

migrations:
	alembic revision --autogenerate -m "$(MSG)"

migrate:
	alembic upgrade head

docker-build:
	docker build -t pix-key-management-api:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api

docker-db-shell:
	docker-compose exec postgres psql -U pix_user -d pix_management_db

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + || true
	find . -type d -name .pytest_cache -exec rm -rf {} + || true
	find . -type d -name .ruff_cache -exec rm -rf {} + || true
	find . -type d -name htmlcov -exec rm -rf {} + || true
	find . -type f -name .coverage -delete || true
