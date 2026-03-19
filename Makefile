PYTHON ?= python
DBT ?= dbt

.PHONY: help install install-dev pipeline artifacts dictionary serve-app serve-api lint format type-check test smoke-dashboard smoke-api smoke-downstream verify package smoke docker-build-app docker-build-api docker-build docker-smoke clean

help:
	@echo "Available targets:"
	@echo "  install            Install runtime dependencies"
	@echo "  install-dev        Install runtime and development dependencies"
	@echo "  pipeline           Run the official batch pipeline"
	@echo "  artifacts          Generate governance artifacts only"
	@echo "  serve-app          Start the Streamlit app"
	@echo "  serve-api          Start the FastAPI service"
	@echo "  lint               Run isort, ruff, and black checks"
	@echo "  format             Apply import sorting, black, and ruff fixes"
	@echo "  type-check         Run mypy"
	@echo "  test               Run pytest"
	@echo "  smoke-dashboard    Run the dashboard smoke check"
	@echo "  smoke-api          Run the FastAPI smoke check"
	@echo "  smoke-downstream   Run the downstream SQL smoke check"
	@echo "  verify             Run the local high-signal validation flow"
	@echo "  package            Build the package"
	@echo "  docker-build       Build both Docker images"
	@echo "  docker-smoke       Smoke-test the batch container"
	@echo "  clean              Remove local tooling caches"

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

smoke-dashboard:
	$(PYTHON) scripts/smoke_dashboard.py

smoke-api:
	$(PYTHON) scripts/smoke_api.py

smoke-downstream:
	$(PYTHON) scripts/smoke_downstream_sql.py

quality: lint type-check test

verify: lint type-check test smoke-dashboard smoke-api smoke-downstream package

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

clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(path, ignore_errors=True) for path in [pathlib.Path('.pytest_cache'), pathlib.Path('.ruff_cache'), pathlib.Path('.mypy_cache'), pathlib.Path('__pycache__')]]"
