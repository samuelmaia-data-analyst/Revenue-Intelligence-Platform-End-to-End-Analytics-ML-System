# Onboarding Guide

## Objective

Get a new contributor from clone to a validated local run quickly, with minimal ambiguity.

## 1. Environment Setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env
```

Recommended interpreter:

- `.venv\Scripts\python.exe`

## 2. First Successful Run

Run the official batch path:

```powershell
python -m src.pipeline run
```

Expected outputs:

- `data/processed/pipeline_manifest.json`
- `data/processed/quality_report.json`
- `data/processed/executive_report.json`
- `data/warehouse/revenue_intelligence.db`

## 3. Validation Commands

```powershell
python -m ruff check .
python -m black --check .
python -m isort --check-only .
python -m mypy src services contracts main.py
python -m pytest -q
python -m build
```

## 4. Optional Interfaces

Dashboard:

```powershell
python -m streamlit run app/streamlit_app.py
```

API:

```powershell
python -m uvicorn services.api.main:app --reload
```

dbt:

```powershell
dbt --project-dir dbt run
```

## 5. Repository Reading Order

Recommended reading sequence:

1. `README.md`
2. `docs/architecture.md`
3. `docs/repository_structure.md`
4. `src/pipeline.py`
5. `src/orchestration.py`

## 6. Common Failure Modes

- Missing dependencies in the active interpreter
  Use `.venv\Scripts\python.exe`
- Empty or stale generated data
  Re-run `python -m src.pipeline run`
- Dashboard load errors
  Confirm processed artifacts exist under `data/processed/`

## 7. Contribution Standard

Before opening a PR:

- keep the batch CLI as the official path
- update docs if runtime behavior changed
- add or update tests for any behavior change
- avoid introducing alternate orchestration paths
