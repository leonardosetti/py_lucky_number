.PHONY: help install test coverage lint format clean build run docker-dev docker-prod

help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies"
	@echo "  test       - Run tests"
	@echo "  coverage   - Run tests with coverage report"
	@echo "  lint       - Run code quality checks"
	@echo "  format     - Format code with black and isort"
	@echo "  clean      - Clean build artifacts"
	@echo "  build      - Build package"
	@echo "  run        - Run development server"
	@echo "  docker-dev - Run with Docker for development"
	@echo "  docker-prod - Run with Docker for production"

install:
	pip install -r requirements-dev.txt
	pip install -e .

test:
	pytest tests/ -v

coverage:
	pytest tests/ --cov=src/lucky_number --cov-report=html --cov-report=term

lint:
	flake8 src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/
	mypy src/lucky_number

format:
	black src/ tests/
	isort src/ tests/

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/ __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

build:
	python -m build

run:
	uvicorn lucky_number.main:app --reload

docker-dev:
	docker-compose up --build

docker-prod:
	docker-compose -f docker-compose.prod.yml up --build -d
