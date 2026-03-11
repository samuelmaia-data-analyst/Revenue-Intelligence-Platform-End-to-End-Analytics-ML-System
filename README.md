# Revenue Intelligence Data Platform

End-to-end analytics platform for revenue intelligence over the Olist e-commerce dataset. The repository packages ingestion, transformation, feature engineering, business KPIs, forecasting, churn modeling, and a Streamlit dashboard behind one official execution surface.

## Quickstart

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
copy .env.example .env
ridp bootstrap-sample-data
ridp run-pipeline all
ridp train-model churn
ridp train-model revenue --periods 3
ridp-dashboard
```

## Problem and solution

The project simulates a small but deliberate modern data platform:

- `raw -> bronze -> silver -> gold` pipeline layering
- KPI marts and customer-level feature generation
- churn and revenue prediction artifacts
- dashboard delivery for business consumption

## Architecture

```text
Data Sources (CSV)
  -> Ingestion
  -> Bronze
  -> Transformation
  -> Silver
  -> Feature Engineering
  -> Gold
  -> Analytics / Models / Dashboard
```

Detailed notes: [docs/architecture.md](/C:/Users/samue/PycharmProjects/Revenue%20Intelligence%20Data%20Platform/docs/architecture.md)

## Repository structure

```text
analytics/   business KPIs and retention metrics
dashboard/   Streamlit application
docs/        architecture and dataset notes
models/      churn and revenue models
pipelines/   bronze, silver and gold generation
ridp/        runtime configuration and CLI entry points
tests/       regression and contract tests
```

## Official commands

```bash
ridp bootstrap-sample-data
ridp run-pipeline ingestion
ridp run-pipeline transformation
ridp run-pipeline features
ridp run-pipeline all
ridp train-model churn
ridp train-model revenue --periods 6
ridp-dashboard
```

Environment overrides:

- `RIDP_RAW_DIR`
- `RIDP_BRONZE_DIR`
- `RIDP_SILVER_DIR`
- `RIDP_GOLD_DIR`
- `RIDP_MODELS_DIR`

## Quality gates

```bash
make format
make lint
make test
pre-commit install
```

CI runs `ruff`, `black --check`, `mypy`, and `pytest` on every push and pull request.

## Dataset

Recommended source: Brazilian E-Commerce Public Dataset by Olist.

- Kaggle: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- Attribution notes: [docs/dataset_source.md](/C:/Users/samue/PycharmProjects/Revenue%20Intelligence%20Data%20Platform/docs/dataset_source.md)

## Troubleshooting

- `Gold layer not found`: run `ridp run-pipeline all` first.
- `DataContractError`: one input table changed schema or is incomplete.
- `No delivered orders found`: the silver layer contains no delivered transactions, so gold KPIs would be invalid.
- import errors in the dashboard: install the project with `python -m pip install -e .[dev]` instead of running from an uninstalled source tree.

## Governance

- Conventional Commits are expected (`feat`, `fix`, `docs`, `chore`, `refactor`, `test`).
- Pull requests and issue templates are available under `.github/`.
- Release history starts in [CHANGELOG.md](/C:/Users/samue/PycharmProjects/Revenue%20Intelligence%20Data%20Platform/CHANGELOG.md).
