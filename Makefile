PYTHON ?= python

install:
	$(PYTHON) -m pip install -e .[dev]

bootstrap:
	$(PYTHON) -m ridp.cli bootstrap-sample-data

pipeline:
	$(PYTHON) -m ridp.cli run-pipeline all

test:
	pytest

lint:
	ruff check .
	black --check .
	mypy .

format:
	ruff check . --fix
	black .

dashboard:
	ridp-dashboard
