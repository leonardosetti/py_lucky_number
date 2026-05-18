.PHONY: help install test coverage lint format clean build run dev migrate backup-build backup-run docker-dev docker-prod

help:
	@echo "Available commands:"
	@echo "  install       - Install dependencies"
	@echo "  dev           - Start development server"
	@echo "  test          - Run tests"
	@echo "  coverage      - Run tests with coverage report"
	@echo "  lint          - Run code quality checks"
	@echo "  format        - Format code with black, isort, ruff"
	@echo "  migrate       - Run Alembic migrations"
	@echo "  migrate-auto  - Auto-generate migration from models"
	@echo "  backup-build  - Build Go backup tool"
	@echo "  clean         - Clean build artifacts"
	@echo "  build         - Build Python package"

install:
	pip install -r requirements-dev.txt
	pip install -e .

dev:
	uvicorn lucky_number.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=src/lucky_number --cov-report=term --cov-fail-under=90

coverage:
	pytest tests/ --cov=src/lucky_number --cov-report=html --cov-report=term --cov-fail-under=90

lint:
	ruff check src/ tests/
	flake8 src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/
	mypy src/lucky_number
	bandit -r src/ -c pyproject.toml

format:
	ruff check --fix src/ tests/
	black src/ tests/
	isort src/ tests/

migrate:
	alembic upgrade head

migrate-auto:
	alembic revision --autogenerate -m "$(msg)"

backup-build:
	cd scripts/backup-tool && go build -o backup-tool .

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/ __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

build:
	python -m build

docker-dev:
	docker compose --profile dev up --build

docker-demo:
	docker compose --profile demo up --build -d

docker-prod:
	docker compose --profile prod up --build -d
