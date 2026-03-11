# Architecture

## Layers

- `pipelines/`: ingestion, transformation and feature engineering stages.
- `analytics/`: KPI and retention calculations over curated gold outputs.
- `models/`: churn classification and revenue forecasting.
- `dashboard/`: Streamlit presentation layer.
- `ridp/`: shared runtime configuration and official CLI entry points.

## Execution flow

```text
raw -> bronze -> silver -> gold -> analytics/models/dashboard
```

## Runtime contract

- Directory locations are configured through `RIDP_*` environment variables.
- The official command surface is the `ridp` CLI plus `ridp-dashboard`.
- Pipeline stages validate required columns before processing data.

## Failure philosophy

- Missing tables fail fast with `FileNotFoundError`.
- Schema drift fails fast with `DataContractError`.
- Gold generation fails when there are no delivered orders, because KPIs would be misleading.
