# Architecture

## Overview

The platform is intentionally small, but the design follows production-minded boundaries:

- `pipelines/` owns movement and transformation between data layers
- `analytics/` reads curated gold outputs only
- `models/` trains from gold features, not from raw extracts
- `dashboard/` is a thin serving layer over curated datasets and the SQLite serving store
- `ridp/` centralizes runtime configuration and CLI entry points

## Layered data flow

```text
raw
  external CSV extracts

bronze
  normalized column names
  ingestion timestamp
  source file lineage

silver
  cleaned conformed tables
  `fct_orders`
  `dim_customers`
  `fct_order_items`

gold
  business KPIs
  customer 360
  churn features
  daily and monthly revenue marts

serving
  SQLite materialization of curated gold outputs
  queryable dashboard-facing datasets
```

## Pipeline stages

### Ingestion

Responsibilities:

- read raw CSV files
- normalize column names
- append ingestion metadata
- persist bronze outputs

Key behavior:

- warns when recommended raw tables are missing
- skips empty raw files instead of producing meaningless bronze tables
- writes dataset metadata sidecars for traceability

### Transformation

Responsibilities:

- validate source contracts
- coerce timestamps and numeric fields
- aggregate payments and order items
- create conformed silver marts

Key behavior:

- fails fast on missing columns
- fails fast on nulls in contract-critical keys
- fails fast on invalid purchase timestamps

### Feature engineering

Responsibilities:

- filter valid delivered orders
- generate revenue marts
- build customer 360 dataset
- derive churn training features and business KPIs

Key behavior:

- refuses to compute KPIs when there are no delivered orders
- uses the latest delivered purchase date as the reference point for recency metrics
- writes metadata sidecars for every gold dataset
- refreshes a SQLite serving store for downstream reads

## Data contracts

The project treats a few invariants as non-negotiable:

- required files must exist
- required columns must exist
- contract-critical identifiers cannot be null
- key timestamps must be parseable
- empty curated datasets should fail when they make downstream metrics misleading

Violations raise `DataContractError` or explicit runtime exceptions with actionable messages.

## Operational traceability

Every generated dataset emits a companion `.metadata.json` file containing:

- dataset name
- pipeline stage
- row count
- column count
- column list
- generation timestamp in UTC
- source tables
- optional `run_id` when execution is triggered through the CLI

CLI-triggered pipeline executions also emit a run manifest under `data/run_manifests/` containing:

- `run_id`
- invoked command and stage
- run timestamps
- produced artifacts grouped by stage
- snapshot artifact locations grouped by stage
- a `snapshot_root` pointing to a preserved copy of that run's outputs

The same execution also updates a lightweight `run_catalog.csv` index and stores physical copies of
produced artifacts under `data/run_artifacts/<run_id>/`. This keeps local operation simple while
still making historical review and recruiter demos deterministic.

A complementary SQLite registry at `data/run_manifests/run_history.db` stores one row per pipeline
execution. This adds a queryable operational layer without requiring an external database service.

Separately, curated gold outputs are materialized into `data/serving/revenue_serving.db`. This
keeps the pipeline local-first while showing a realistic boundary between batch data production and
serving/query consumption.

This is intentionally simple, but it gives reviewers evidence of lineage and makes local debugging easier.

## Configuration model

Runtime configuration is environment-driven and centralized in `ridp/config.py`.

Supported environment variables:

- `RIDP_RAW_DIR`
- `RIDP_BRONZE_DIR`
- `RIDP_SILVER_DIR`
- `RIDP_GOLD_DIR`
- `RIDP_SERVING_DB`
- `RIDP_MODELS_DIR`
- `RIDP_RUNS_DIR`
- `RIDP_RUN_ARTIFACTS_DIR`
- `RIDP_RUN_HISTORY_DB`
- `RIDP_LOG_LEVEL`
- `RIDP_DASHBOARD_DEMO_MODE`
- `RIDP_DASHBOARD_DEMO_ASSETS_DIR`

## Failure philosophy

- Prefer loud failures over silent corruption.
- Reject misleading outputs instead of producing incomplete gold tables.
- Keep exception messages operator-friendly and directly tied to the failing dataset.

## Intentional non-goals

This repository does not currently include:

- workflow orchestration with Airflow, Dagster, or Prefect
- object storage or warehouse-backed persistence
- streaming execution
- advanced feature store or model registry integration

Those omissions are deliberate. The current scope focuses on demonstrating disciplined engineering fundamentals in a repository that remains easy to inspect during portfolio review.
