# Revenue Intelligence Data Platform

Production-oriented analytics engineering project over the Olist e-commerce dataset. The repository implements a small but disciplined data platform with `raw -> bronze -> silver -> gold` layers, contract-aware transformations, model training entry points, and a Streamlit serving layer behind a single CLI surface.

## Why this project matters

This project is designed to demonstrate practical senior-level data engineering concerns, not just notebook analysis:

- reproducible local execution through a packaged CLI
- explicit data contracts and fast failure on schema drift
- separation between ingestion, transformation, feature engineering, analytics, models, and serving
- operational traceability through logging, per-dataset metadata sidecars, and run manifests
- lightweight SQL serving store for curated outputs and dashboard reads
- automated quality gates with lint, typing, tests, and CI

## Business problem

Revenue teams need reliable answers to questions such as:

- How much GMV is the business generating over time?
- Which customers are becoming inactive or likely to churn?
- How do retention and customer value evolve across cohorts?
- Can the team forecast short-term revenue using curated marts instead of raw extracts?

The platform turns raw CSV extracts from the Olist dataset into curated analytical assets, lightweight model outputs, and dashboard-ready tables.

## Architecture

```text
Raw CSV extracts
  -> ingestion pipeline
  -> bronze tables + metadata
  -> transformation pipeline
  -> silver marts + metadata
  -> feature pipeline
  -> gold datasets + metadata
  -> analytics metrics / model training / dashboard
```

Detailed references:

- [Architecture](docs/architecture.md)
- [Dataset source notes](docs/dataset_source.md)
- [Runbook and onboarding](docs/runbook.md)

## Technical highlights

- Contract-aware CSV readers validate required columns and fail loudly on invalid states.
- Pipeline outputs write companion `.metadata.json` files with stage, schema, row count, sources, and generation timestamp.
- The CLI centralizes environment-based configuration and logging.
- The Streamlit app now uses a multipage workspace for executive KPIs, customer segmentation, operational artifact health, and run-history comparison.
- Tests cover end-to-end flow, contract failures, invalid timestamps, and model artifact generation.
- Repository automation includes `Makefile`, `pre-commit`, GitHub Actions, issue templates, and PR template.

## Product preview

The Streamlit workspace is structured as a small analytics product rather than a single demo page:

- `Executive Overview`: KPI deck, trend analysis, cohort retention, and business-readout summaries
- `Customer Health`: customer segmentation, high-value risk detection, and searchable `customer_360`
- `Operations`: artifact freshness, metadata-backed dataset health, and operational notes
- `Run History`: manifest comparison across pipeline runs and artifact-level traceability

Screenshot slots are prepared under `docs/assets/dashboard/` for portfolio-ready captures:

- `docs/assets/dashboard/overview.png`
- `docs/assets/dashboard/customer-health.png`
- `docs/assets/dashboard/operations.png`
- `docs/assets/dashboard/run-history.png`

### Executive Overview

![Executive Overview](docs/assets/dashboard/overview.png)

### Customer Health

![Customer Health](docs/assets/dashboard/customer-health.png)

### Operations

![Operations](docs/assets/dashboard/operations.png)

### Run History

![Run History](docs/assets/dashboard/run-history.png)

Suggested capture flow:

```bash
set RIDP_DASHBOARD_DEMO_MODE=ON
ridp-dashboard
```

Then capture the four pages above in a desktop viewport and commit them alongside the README update.

## Repository structure

```text
analytics/   KPI and retention metrics over gold outputs
dashboard/   Streamlit application
docs/        architecture, dataset notes, and runbook
models/      churn and revenue forecasting training flows
pipelines/   ingestion, transformation, feature engineering, shared contracts
ridp/        runtime configuration, CLI, dashboard launcher
tests/       regression and contract-oriented tests
```

## Stack

- Python 3.11+
- pandas
- scikit-learn
- Streamlit
- pytest
- ruff
- black
- mypy
- GitHub Actions

## Quickstart

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
copy .env.example .env
make bootstrap
make pipeline
ridp train-model churn
ridp train-model revenue --periods 3
make dashboard
```

## Configuration

Environment variables are optional and default to project-local paths:

```bash
RIDP_RAW_DIR=data/raw
RIDP_BRONZE_DIR=data/bronze
RIDP_SILVER_DIR=data/silver
RIDP_GOLD_DIR=data/gold
RIDP_SERVING_DB=data/serving/revenue_serving.db
RIDP_MODELS_DIR=models/artifacts
RIDP_RUNS_DIR=data/run_manifests
RIDP_RUN_ARTIFACTS_DIR=data/run_artifacts
RIDP_RUN_HISTORY_DB=data/run_manifests/run_history.db
RIDP_LOG_LEVEL=INFO
RIDP_FRESHNESS_SLA_HOURS=24
RIDP_DASHBOARD_DEMO_MODE=AUTO
RIDP_DASHBOARD_DEMO_ASSETS_DIR=dashboard/demo_assets
```

Dashboard demo behavior:

- `AUTO`: use real curated outputs when available, otherwise fall back to bundled demo assets
- `ON`: force bundled demo assets for portfolio walkthroughs
- `OFF`: require real pipeline outputs only
- The Streamlit sidebar exposes the same behavior as `Workspace Source`, so reviewers can switch between `Auto`, `Live Data`, and `Demo Data` without editing environment variables.

## Execution surfaces

Official commands:

```bash
ridp bootstrap-sample-data
ridp run-pipeline ingestion
ridp run-pipeline transformation
ridp run-pipeline features
ridp run-pipeline all
ridp run-pipeline all --run-id portfolio-demo-001
ridp check-health
ridp check-health --strict
ridp train-model churn
ridp train-model revenue --periods 6
ridp-dashboard
```

If you want a predictable portfolio walkthrough without bootstrapping data first:

```bash
set RIDP_DASHBOARD_DEMO_MODE=ON
ridp-dashboard
```

Make targets:

```bash
make install
make bootstrap
make pipeline
make health
make lint
make test
make build
make check
make format
make dashboard
```

When `.venv` exists, `make` commands automatically prefer that interpreter over the global Python.
`requirements.txt` is kept as a lightweight runtime compatibility artifact and should mirror the
runtime dependencies declared in `pyproject.toml`.

## Data flow and outputs

`bronze`

- normalized source column names
- ingestion timestamp and source file lineage

`silver`

- `fct_orders.csv`
- `dim_customers.csv`
- `fct_order_items.csv`

`gold`

- `kpi_daily_revenue.csv`
- `kpi_monthly_revenue.csv`
- `customer_360.csv`
- `churn_features.csv`
- `business_kpis.csv`

`serving`

- `revenue_serving.db`
- SQLite materialization of curated gold outputs for lightweight SQL reads

Each generated dataset also emits a `.metadata.json` file with schema and lineage context.

CLI-triggered pipeline runs also emit a manifest under `data/run_manifests/` with a shared
`run_id`, execution timestamps, and the artifacts produced by each stage.

Each CLI run also snapshots stage outputs under `data/run_artifacts/<run_id>/` and updates
`data/run_manifests/run_catalog.csv` for a lightweight execution index.
The same run is also registered in `data/run_manifests/run_history.db`, making execution history
queryable through SQLite.
Gold outputs are also materialized into `data/serving/revenue_serving.db` so curated datasets are
available through a stable SQL serving layer.

## Reliability and quality posture

- Missing files raise `FileNotFoundError`.
- Schema drift and nulls in contract-critical columns raise `DataContractError`.
- Invalid order timestamps fail transformation explicitly.
- Gold generation refuses to compute KPIs when there are no delivered orders.
- Churn training degrades gracefully when the target is not trainable.
- CLI pipeline runs can be traced end-to-end through a shared `run_id`.
- CLI pipeline runs preserve per-stage snapshot artifacts for deterministic run review.
- CLI pipeline runs are also registered in a lightweight SQLite operations store.
- `ridp check-health` validates required gold artifacts, metadata sidecars, freshness SLA, and local serving/runtime readiness.
- Dashboard startup is deterministic through an official demo mode with bundled curated assets.

## Validation

```bash
make lint
make test
```

CI runs on every push and pull request and executes:

- `ruff check .`
- `black --check .`
- `mypy .`
- `pytest`
- `python -m build --sdist --wheel`

## Trade-offs

- Storage is local filesystem based, intentionally keeping orchestration simple for portfolio readability.
- Forecasting and churn models are lightweight baselines, chosen to emphasize pipeline discipline and artifact management over model sophistication.
- The project favors explicit pandas transformations over framework-heavy orchestration to keep the engineering signal easy to inspect.

## Recruiter / reviewer signal

This repository is meant to communicate:

- clear separation of concerns
- operational thinking around contracts, failures, and reproducibility
- pragmatic automation instead of notebook-only experimentation
- code that is readable, testable, and maintainable by another engineer

## Contributing

Collaboration guidance lives in [CONTRIBUTING.md](CONTRIBUTING.md).

## Roadmap

- add richer data quality assertions and anomaly checks
- persist model artifacts in a more portable serialization format
- expand dashboard drill-downs and operational status views
- add batch execution snapshots and historical run comparisons
