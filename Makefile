PYTHON ?= python

.PHONY: install install-dev pipeline serve-app serve-api lint format test quality docker-build-app docker-build-api docker-build

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

install-dev: install
	$(PYTHON) -m pip install -r requirements-dev.txt

pipeline:
	$(PYTHON) -m src.pipeline run

serve-app:
	$(PYTHON) -m streamlit run app/streamlit_app.py

serve-api:
	$(PYTHON) -m uvicorn services.api.main:app --host 0.0.0.0 --port 8000 --reload

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m black --check .

format:
	$(PYTHON) -m black .
	$(PYTHON) -m ruff check . --fix

test:
	$(PYTHON) -m pytest -q

quality: lint test

docker-build-app:
	docker build -t revenue-intelligence .

docker-build-api:
	docker build -f Dockerfile.api -t revenue-intelligence-api .

docker-build: docker-build-app docker-build-api
