PYTHON ?= python

install:
	$(PYTHON) -m pip install -e .[dev]

bootstrap:
	$(PYTHON) -m ridp.cli bootstrap-sample-data

pipeline:
	$(PYTHON) -m ridp.cli run-pipeline all

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m black --check .
	$(PYTHON) -m mypy .

format:
	$(PYTHON) -m ruff check . --fix
	$(PYTHON) -m black .

dashboard:
	ridp-dashboard
