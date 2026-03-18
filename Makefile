PYTHON ?= python
DBT ?= dbt

.PHONY: install install-dev pipeline artifacts dictionary serve-app serve-api lint format type-check test quality package smoke docker-build-app docker-build-api docker-build docker-smoke

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

install-dev: install
	$(PYTHON) -m pip install -r requirements-dev.txt

pipeline:
	$(PYTHON) -m src.pipeline run

artifacts: dictionary

dictionary:
	$(PYTHON) -m src.pipeline artifacts

serve-app:
	$(PYTHON) -m streamlit run app/streamlit_app.py

serve-api:
	$(PYTHON) -m uvicorn services.api.main:app --host 0.0.0.0 --port 8000 --reload

lint:
	$(PYTHON) -m isort --check-only .
	$(PYTHON) -m ruff check .
	$(PYTHON) -m black --check .

format:
	$(PYTHON) -m isort .
	$(PYTHON) -m black .
	$(PYTHON) -m ruff check . --fix

type-check:
	$(PYTHON) -m mypy src services contracts main.py

test:
	$(PYTHON) -m pytest -q

quality: lint type-check test

package:
	$(PYTHON) -m build

smoke:
	$(PYTHON) -m src.pipeline run --log-level INFO

dbt-run:
	$(DBT) --project-dir dbt run

dbt-test:
	$(DBT) --project-dir dbt test

dbt-docs:
	$(DBT) --project-dir dbt docs generate

docker-build-app:
	docker build -t revenue-intelligence .

docker-build-api:
	docker build -f Dockerfile.api -t revenue-intelligence-api .

docker-build: docker-build-app docker-build-api

docker-smoke:
	docker run --rm revenue-intelligence python -m src.pipeline run --log-level INFO
