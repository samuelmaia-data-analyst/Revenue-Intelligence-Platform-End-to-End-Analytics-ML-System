# Revenue Intelligence Platform

Production-minded batch analytics platform that turns customer behavior data into reproducible revenue intelligence outputs.

This repository is intentionally small. The goal is not to simulate a large enterprise stack. The goal is to show disciplined engineering around a realistic analytics workflow: ingest, validate, curate, score, report, persist, and trace every run.

[Portuguese version](README.pt-BR.md)

## What This Repository Demonstrates

- a single official batch pipeline entrypoint
- reprocessable and deterministic curated outputs
- run-level manifests, logs, snapshots, and retention
- atomic writes for critical artifacts
- environment-driven configuration via `.env`
- lightweight but real governance through contracts and generated dictionary
- quality gates that include lint, formatting, type-checking, tests, package build, and container validation

## System Scope

The platform transforms raw customer and order behavior into:

- churn risk scores
- next-purchase propensity
- channel efficiency and unit economics
- cohort retention outputs
- executive KPI snapshots
- prioritized action recommendations
- queryable warehouse tables

This is a batch-first system. Streamlit, FastAPI, dbt, Airflow, and Prefect are optional consumers or wrappers around the batch core, not competing sources of orchestration truth.

## Official Operating Path

Run the pipeline with:

```powershell
python -m src.pipeline run
```

That command is the primary supported execution path.

Key modules:

- [src/pipeline.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/pipeline.py): CLI
- [src/orchestration.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/orchestration.py): end-to-end pipeline
- [src/config.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/config.py): runtime configuration
- [src/ingestion.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/ingestion.py): raw and bronze ingestion
- [src/transformation.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/transformation.py): silver validation and feature engineering
- [src/modeling.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/modeling.py): training, scoring, and model registry
- [src/reporting.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/reporting.py): executive artifacts
- [src/persistence.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/persistence.py): warehouse persistence
- [src/governance.py](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/governance.py): generated governance assets

## Architecture

```text
raw input
  -> ingestion
  -> bronze
  -> silver validation
  -> customer features
  -> gold warehouse tables
  -> ML scoring
  -> curated metrics and recommendations
  -> reporting artifacts
  -> manifests, logs, snapshots, retention
```

Architecture notes:

- the project uses explicit file-based layers because they are reproducible and easy to inspect locally
- SQLite is the default warehouse target because it keeps the system runnable without external infrastructure
- governance is intentionally lightweight and focused on the highest-signal outputs

See [docs/architecture.md](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/docs/architecture.md) and [docs/repository_structure.md](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/docs/repository_structure.md).

## Operational Outputs

One successful run produces, at minimum:

- `data/processed/pipeline_manifest.json`
- `data/processed/raw_input_metadata.json`
- `data/processed/quality_report.json`
- `data/processed/freshness_report.json`
- `data/processed/kpi_snapshot.json`
- `data/processed/data_dictionary.json`
- `data/warehouse/revenue_intelligence.db`
- `data/runs/<run_id>/pipeline.log`
- `data/snapshots/<run_id>/`
- `data/manifests/<run_id>.success.json`

If a run fails, the pipeline emits:

- `data/manifests/<run_id>.failure.json`

## Reliability Model

The repository is designed to show disciplined batch operation, not just business logic.

Implemented controls:

- atomic CSV and JSON writes
- atomic SQLite replacement
- explicit `run_id`
- input fingerprinting
- raw input metadata snapshots
- source-aware freshness checks
- success and failure manifests
- snapshot retention by count and age
- failure manifest retention by age

## Local Setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env
python -m src.pipeline run
```

Useful commands:

```powershell
make pipeline
make dictionary
make lint
make type-check
make test
make quality
make package
```

## Configuration

Runtime settings are loaded from `.env` and environment variables.

Important variables:

- `RIP_ENV`
- `RIP_DATA_DIR`
- `RIP_SEED`
- `RIP_LOG_LEVEL`
- `RIP_FRESHNESS_MAX_AGE_HOURS`
- `RIP_SNAPSHOT_RETENTION_RUNS`
- `RIP_SNAPSHOT_RETENTION_DAYS`
- `RIP_FAILURE_RETENTION_DAYS`
- `RIP_WAREHOUSE_TARGET`
- `RIP_WAREHOUSE_URL`
- `RIP_SEMANTIC_METRICS_PATH`

Reference template:

- [.env.example](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/.env.example)

## Quality Standards

The repository is expected to stay green on:

- `ruff`
- `black`
- `isort`
- `mypy`
- `pytest`
- `build`

CI also validates:

- Docker image build
- container smoke execution of the official CLI
- upload of smoke-run artifacts

## Optional Interfaces

Optional interfaces exist, but they are secondary to the batch core:

- Streamlit UI: `python -m streamlit run app/streamlit_app.py`
- FastAPI service: `python -m uvicorn services.api.main:app --reload`
- dbt project: `dbt --project-dir dbt run`
- Airflow and Prefect examples in `orchestration/`

## Contributing

Use the repository as a small production-minded system, not as a dumping ground for features.

Read:

- [CONTRIBUTING.md](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/CONTRIBUTING.md)
- [.github/pull_request_template.md](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/.github/pull_request_template.md)

## Technical Trade-offs

- scikit-learn baselines are sufficient for the intended scope, but this is not presented as a large-scale online serving system
- file-based governance improves reproducibility, but it is not a substitute for a full metadata platform
- scheduler examples exist for operational flavor, but the repository remains CLI-first by design

## Roadmap

Near-term upgrade track:

- explicit backfill window support in CLI
- proportional retry for failure-prone stages
- one additional governed upstream contract surface
- stage-level modularization of the pipeline core
- tighter package boundaries around the batch core

Tracking artifacts:

- [docs/staff_upgrade_master_issue.md](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/docs/staff_upgrade_master_issue.md)
- [docs/issues/project_board.md](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/docs/issues/project_board.md)
