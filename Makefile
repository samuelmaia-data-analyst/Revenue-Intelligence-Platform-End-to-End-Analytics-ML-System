.PHONY: install bootstrap pipeline health test lint build check format precommit dashboard

ifeq ($(OS),Windows_NT)
VENV_PYTHON := .venv\Scripts\python.exe
else
VENV_PYTHON := .venv/bin/python
endif

ifneq ($(wildcard $(VENV_PYTHON)),)
PYTHON ?= $(VENV_PYTHON)
else
PYTHON ?= python
endif

install:
	$(PYTHON) -m pip install -e .[dev]

bootstrap:
	$(PYTHON) -m ridp.cli bootstrap-sample-data

pipeline:
	$(PYTHON) -m ridp.cli run-pipeline all

health:
	$(PYTHON) -m ridp.cli check-health

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m black --check .
	$(PYTHON) -m mypy .

build:
	$(PYTHON) -m build --sdist --wheel

check: lint test build

format:
	$(PYTHON) -m ruff check . --fix
	$(PYTHON) -m black .

precommit:
	$(PYTHON) -m pre_commit run --all-files

dashboard:
	ridp-dashboard
