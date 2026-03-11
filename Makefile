PYTHON ?= python

.PHONY: install install-dev pipeline serve-app serve-api lint format typecheck test test-cov quality docker-build-app docker-build-api docker-build

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .

install-dev: install
	$(PYTHON) -m pip install -e .[dev]

pipeline:
	rip-pipeline run

serve-app:
	rip-app

serve-api:
	rip-api

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m black --check .

format:
	$(PYTHON) -m black .
	$(PYTHON) -m ruff check . --fix

typecheck:
	$(PYTHON) -m mypy src services

test:
	$(PYTHON) -m pytest

test-cov:
	$(PYTHON) -m pytest --cov=src --cov=services --cov-report=term-missing --cov-fail-under=85

quality: lint typecheck test

docker-build-app:
	docker build -t revenue-intelligence .

docker-build-api:
	docker build -f Dockerfile.api -t revenue-intelligence-api .

docker-build: docker-build-app docker-build-api
