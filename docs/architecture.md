# Architecture Overview

## Goal

Provide a reproducible revenue intelligence workflow with explicit separation between data preparation, analytics, machine learning, and executive insight generation.

## Pipeline Layers

### 1. Raw

- source dataset in `data/raw/`
- deterministic fallback generation when the external file is unavailable

### 2. Bronze

- auditable ingestion layer
- preserves source lineage with `_source_file` and `_ingestion_ts`

### 3. Silver

- standardized types
- required-column validation
- deduplication
- null filtering
- referential cleanup between customers and orders

### 4. Gold

- star schema with:
  - `dim_customers.csv`
  - `dim_date.csv`
  - `dim_channel.csv`
  - `fact_orders.csv`

### 5. Analytics

- centralized KPI computation:
  - LTV
  - CAC
  - RFM
  - cohort retention
  - unit economics
  - KPI snapshot

### 6. ML

- feature engineering at customer level
- churn model
- next purchase model
- temporal evaluation
- model registry
- business-facing driver summaries

### 7. Insights

- recommendations
- executive report
- executive summary
- business outcomes simulation
- dashboard/API consumption layer

## Reproducibility Controls

- `PipelineConfig` controls runtime paths, seed, and log level
- `pipeline_manifest.json` records execution metadata and output inventory
- `quality_report.json` records basic data quality diagnostics
- versioned model registry tracks latest production artifacts
