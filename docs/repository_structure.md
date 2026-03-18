# Repository Structure

## Intent

This repository is organized around one central idea: the batch pipeline is the productized core.

Everything else should either support that core, validate it, or consume its outputs.

## Top-Level Layout

```text
.
|- .github/            CI workflows, issue templates, PR template
|- api/                Compatibility shim for API imports
|- app/                Streamlit UI
|- contracts/          Versioned contracts and compatibility shims
|- data/               Local data, generated artifacts, manifests, snapshots, warehouse
|- dbt/                dbt models and governance assets over the warehouse
|- docs/               Architecture, planning, issues, release notes, structure docs
|- metrics/            Declarative semantic metric definitions
|- orchestration/      Optional scheduler examples
|- services/           Runtime service interfaces
|- src/                Core pipeline and domain logic
|- tests/              Automated tests
```

## Directory Responsibilities

### `src/`

Authoritative home for:

- ingestion
- validation
- transformation
- modeling
- reporting
- governance generation
- persistence
- orchestration
- CLI

Rule:
- business logic belongs here first

### `services/`

Runtime-facing service interfaces.

Current use:

- `services/api/` for FastAPI serving

Rule:
- services should consume or expose the core, not duplicate it

### `contracts/`

Governed schemas and compatibility layers.

Current pattern:

- `contracts/v1/` contains the current contract version
- `contracts/data_contract.py` preserves a stable import path

Rule:
- new governed contracts should be versioned deliberately

### `app/`

Visualization and presentation layer.

Rule:
- UI should consume generated artifacts or warehouse outputs rather than reimplement pipeline logic

### `dbt/`

Semantic and warehouse-oriented modeling on top of persisted tables.

Rule:
- dbt is downstream of the batch core

### `orchestration/`

Scheduler examples and deployment-oriented wrappers.

Rule:
- orchestration examples must call the official batch path instead of inventing a second orchestration model

### `data/`

Local runtime state.

Important subdirectories:

- `raw/`
- `bronze/`
- `silver/`
- `gold/`
- `processed/`
- `warehouse/`
- `manifests/`
- `runs/`
- `snapshots/`

Rule:
- treat `data/` as runtime output, not as a place for source code or permanent documentation

### `tests/`

Regression coverage for:

- pipeline behavior
- contracts
- operational artifacts
- API behavior
- warehouse persistence
- reliability controls

Rule:
- tests should validate behavior, not just file existence, when practical

## Import Policy

Preferred imports:

- contracts from `contracts.v1.data_contract`
- API entrypoint from `services.api`

Compatibility shims:

- `api/`
- `contracts/data_contract.py`
- `src/data_contract.py`

Rule:
- use shims only where backward compatibility matters

## Placement Rules

When adding a new component:

1. put domain behavior in `src/`
2. put governed schemas in `contracts/`
3. add tests in `tests/`
4. update docs if runtime behavior changed
5. keep batch CLI as the system's primary entrypoint

## Anti-Patterns

Avoid:

- putting orchestration logic in UI or API modules
- documenting architecture that the code does not implement
- creating new top-level directories without a boundary reason
- duplicating business logic across `src/`, `app/`, and `services/`

## Maintenance Rule

If the repository grows, prefer sharpening boundaries over adding more layers.

A small repository with clear ownership is stronger than a large repository with decorative structure.
