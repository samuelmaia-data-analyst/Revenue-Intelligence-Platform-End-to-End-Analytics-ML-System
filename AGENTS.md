# AGENTS.md

## Purpose

This repository contains an end-to-end revenue intelligence data platform over the Olist dataset. Changes should preserve the integrity of the pipeline flow, model training entry points, and dashboard usability.

## Source Of Truth

- Treat `README.md` as the primary project overview and operator-facing setup guide.
- Treat `pyproject.toml` as the source of truth for Python version, dependencies, tooling, and CLI entry points.
- Treat `Makefile` as the preferred shorthand for common local quality checks.

## Environment

- Use Python `3.11+`.
- Prefer a local virtual environment in `.venv`.
- Install dependencies with `python -m pip install -e .[dev]`.
- If environment variables are needed, start from `.env.example`.

## Repository Map

- `ridp/`: runtime configuration, CLI, and dashboard launcher.
- `pipelines/`: ingestion, bronze/silver/gold, and feature generation logic.
- `analytics/`: KPI and retention analytics.
- `models/`: churn and revenue forecasting training code.
- `dashboard/`: Streamlit application.
- `tests/`: regression and contract-oriented tests.
- `docs/`: architecture and dataset notes.

## Preferred Commands

- Install: `make install`
- Bootstrap sample data: `make bootstrap`
- Run full pipeline: `make pipeline`
- Run dashboard: `make dashboard`
- Run tests: `make test`
- Run lint checks: `make lint`
- Auto-format: `make format`

When validating a change, prefer the narrowest command that proves correctness, then run broader checks if the change crosses module boundaries.

## Change Rules

- Keep changes focused on the user request. Do not mix refactors with behavior changes unless required.
- Preserve public CLI behavior unless the task explicitly requires changing it.
- Prefer fixing logic at the source rather than adding compensating workarounds.
- Avoid introducing new dependencies unless they are clearly justified by the task.
- Keep file and function names consistent with the current project style.

## Data And Pipeline Safety

- Be careful with assumptions about dataset completeness and schema. Existing tests and errors indicate the project expects contract-like behavior.
- Do not silently swallow missing-column, empty-data, or invalid-state conditions that should fail loudly.
- If changing pipeline outputs or schema, update the affected tests and any downstream code that consumes those artifacts.

## Models And Analytics

- Keep churn and revenue training flows callable through the existing `ridp` CLI surface.
- Prefer deterministic transformations where practical so tests remain stable.
- If a model-related change alters features, inputs, or output artifact names, document the impact in code or tests.

## Dashboard

- Preserve compatibility with `ridp-dashboard`.
- Favor changes that degrade gracefully when expected artifacts are missing, but do not hide actionable failures from the operator.

## Validation Expectations

Use the smallest relevant subset first:

- Formatting-only change: `make format`
- Logic change in Python modules: `make test`
- Cross-cutting or release-ready change: `make lint` and `make test`

If you cannot run a needed validation command, state that clearly in your handoff.

## Documentation Expectations

- Update `README.md` when changing setup steps, CLI usage, or operator-visible behavior.
- Update `docs/` when changing architecture, data flow, or dataset assumptions that are not obvious from code.

## Handoff

Final responses should state:

- what changed,
- how it was validated,
- any remaining risks or unverified paths.
