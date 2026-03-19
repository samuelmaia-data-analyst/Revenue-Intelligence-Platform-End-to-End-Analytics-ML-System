# ADR 0001: Batch Pipeline Is the System of Record

## Status

Accepted

## Context

This repository includes multiple consumption surfaces:

- batch pipeline
- Streamlit dashboard
- API layer
- dbt project
- orchestration examples

Without a clear center of gravity, portfolio repositories often drift into duplicated logic and unclear ownership.

## Decision

The official batch pipeline, executed through `python -m src.pipeline run`, is the only authoritative runtime path.

All other interfaces must consume its outputs or the warehouse produced by it.

## Consequences

Positive:

- one place to enforce quality, retry, contracts and observability
- simpler debugging and operational ownership
- less risk of divergent business logic across interfaces

Negative:

- UI and API changes are constrained by batch output shape
- some interactive scenarios must wait for batch outputs instead of recomputing live

## Why This Is Worth It

For a production-minded analytics portfolio, operational clarity is more valuable than pretending to support many equal execution paths.
