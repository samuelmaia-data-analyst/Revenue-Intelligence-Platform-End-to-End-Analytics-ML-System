# Runbook

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
copy .env.example .env
```

## Bootstrap and execute

```bash
make bootstrap
make pipeline
ridp run-pipeline all --run-id local-debug-001
ridp train-model churn
ridp train-model revenue --periods 3
ridp-dashboard
```

For a deterministic portfolio demo without running the pipeline first:

```bash
set RIDP_DASHBOARD_DEMO_MODE=ON
ridp-dashboard
```

## Expected artifacts

After `make pipeline`:

- `data/bronze/*.csv`
- `data/silver/*.csv`
- `data/gold/*.csv`
- matching `*.metadata.json` files for generated datasets
- `data/run_manifests/*.json` for CLI-triggered runs
- `data/serving/revenue_serving.db` for SQL-oriented serving reads

After model training:

- `models/artifacts/churn_metrics.json`
- `models/artifacts/churn_model_coefficients.json`
- `models/artifacts/revenue_forecast.csv`
- `models/artifacts/revenue_forecast_metrics.json`
- `models/artifacts/revenue_forecast_model.json`

## Quality checks

```bash
make lint
make test
pre-commit install
```

If `.venv` exists, the Makefile automatically uses that interpreter for local commands.

## Run traceability

When the pipeline is launched through the CLI, use `--run-id` to correlate all outputs from a
single execution:

```bash
ridp run-pipeline all --run-id portfolio-demo-001
```

Expected traceability:

- every generated dataset metadata file contains the same `run_id`
- `data/run_manifests/<run_id>.json` lists artifacts written by each pipeline stage
- `data/run_artifacts/<run_id>/` preserves a physical copy of stage outputs for that run
- `data/run_manifests/run_catalog.csv` keeps a simple index of recent executions
- `data/run_manifests/run_history.db` stores the same run history in SQLite for ad hoc queries

## Dashboard source modes

The Streamlit workspace can run against either the primary curated outputs or bundled demo assets.

- `RIDP_DASHBOARD_DEMO_MODE=AUTO`: prefer real gold outputs and fall back to `dashboard/demo_assets`
- `RIDP_DASHBOARD_DEMO_MODE=ON`: force the bundled demo assets
- `RIDP_DASHBOARD_DEMO_MODE=OFF`: fail unless the real gold layer exists

## Failure scenarios

### Missing source file

Symptom:

- `FileNotFoundError` referencing a required table

Likely cause:

- raw or intermediate layer not generated yet

Operator action:

- rerun the prior stage or the full pipeline with `ridp run-pipeline all`

### Contract drift

Symptom:

- `DataContractError` mentioning missing columns or nulls in required columns

Likely cause:

- source schema changed or an upstream file is incomplete

Operator action:

- inspect the failing dataset and restore the expected contract before rerunning

### Invalid timestamps

Symptom:

- transformation fails on `order_purchase_timestamp`

Likely cause:

- malformed source values in `olist_orders_dataset.csv`

Operator action:

- correct source data or filter invalid rows before ingestion

### Empty delivered order set

Symptom:

- feature engineering raises `No delivered orders found`

Likely cause:

- silver layer contains only canceled, pending, or otherwise non-delivered orders

Operator action:

- verify the transformation inputs and business assumptions before generating gold outputs

## Maintenance notes

- Keep changes scoped to the existing CLI surface unless a behavior change is intentional and documented.
- Update tests when contracts or output schemas change.
- Update `README.md` and `docs/architecture.md` when execution flow or operator-facing behavior changes.
