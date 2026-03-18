# Architecture Overview

## Objective

Keep the project small enough for a portfolio repository while still behaving like a credible analytical batch system.

## Official Execution Path

The official entrypoint is:

```powershell
python -m src.pipeline run
```

That command executes the end-to-end pipeline in [`src/orchestration.py`](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/src/orchestration.py).

## Layered Flow

1. `raw`
   Source CSV is read from `data/raw/` when present, otherwise deterministic synthetic data is generated.
2. `bronze`
   Raw tables are copied with ingestion metadata for lineage.
3. `silver`
   Required-column validation, deduplication, type normalization and referential cleanup.
4. `features`
   Customer-level analytical base with recency, frequency, monetary, tenure, ARPU and future targets.
5. `gold`
   Curated star schema with `dim_customers`, `dim_date`, `dim_channel` and `fact_orders`.
6. `metrics`
   LTV, CAC, RFM, cohort retention, unit economics, recommendations and KPI snapshot.
7. `modeling`
   Churn and next-purchase models, scoring and model registry update.
8. `reporting`
   Executive report, executive summary and prioritized action simulation.
9. `operations`
   Warehouse persistence, raw input metadata, manifests, logs, snapshots, freshness checks and retention.

## Reliability Controls

- `run_id` for each execution
- input fingerprint for traceability
- raw input metadata with source timestamps and dataset fingerprints
- atomic writes for CSV/JSON outputs
- atomic SQLite replacement
- success manifest
- failure manifest
- historical snapshot per run
- retention by quantity and age
- centralized run log with contextual `run_id`

## Governance

- curated output contracts in [`contracts/v1/data_contract.py`](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/contracts/v1/data_contract.py)
- generated data dictionary in `data/processed/data_dictionary.json`
- semantic metrics catalog generated from `metrics/semantic_metrics.json`

## Intentional Constraints

- SQLite is the default warehouse to preserve reproducibility.
- Orchestration is code-first and local-first; scheduler examples remain optional wrappers.
- Governance is lightweight and focused on curated outputs instead of modeling every file in the repository.
