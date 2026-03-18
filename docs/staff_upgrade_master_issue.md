# Master Issue: Elevate Revenue Intelligence Platform to Production-Minded Portfolio Standard

## Objective

Push this repository from a strong portfolio project to a small, serious, production-minded data platform that holds up under senior engineering review.

This issue is intentionally focused on engineering credibility, not cosmetic expansion.

## Current Position

The repository now has:

- one official batch pipeline entrypoint
- run-level manifests and snapshots
- atomic writes for core artifacts
- idempotent curated outputs
- environment-driven runtime configuration
- generated governance artifacts
- working quality toolchain
- Docker/package/CI validation

What still separates it from a top-tier `9.5+/10` portfolio signal is not feature count. It is stronger operational proof, tighter data lifecycle discipline, and sharper evidence that architecture decisions remain coherent as the system grows.

## Success Criteria

This issue is done when the repository demonstrates all of the following without aspirational documentation:

- deterministic batch reprocessing with explicit backfill semantics
- source-aware freshness and dataset version traceability
- operationally defensible container execution path
- tighter warehouse and integration validation
- governance that expands only where it improves reliability
- documentation that remains fully faithful to implemented behavior

## Guiding Principles

- prefer clarity over framework accumulation
- prefer reproducibility over convenience
- prefer traceability over implicit behavior
- do not add enterprise theater
- only add complexity that materially reduces risk or improves maintainability

## Priority Backlog

### P0: Operational Credibility

- [ ] Add a real container smoke test workflow that runs the official CLI and asserts expected artifacts.
  - Why: current Docker build validation is useful, but strong portfolio signal comes from proving the container actually executes the batch path.
  - Acceptance criteria:
    - CI runs containerized pipeline execution
    - workflow asserts presence of core outputs and manifest
    - failure exits non-zero with clear logs

- [ ] Add a dedicated integration test for SQLite warehouse contents after one full pipeline run.
  - Why: right now warehouse persistence is validated mainly by file existence and indirect behavior.
  - Acceptance criteria:
    - test opens generated SQLite database
    - validates table set and row counts are non-zero where expected
    - validates at least one join path across curated tables

- [ ] Add run artifact assertions to CI output or uploaded artifacts.
  - Why: manifests and snapshots are more credible when CI exposes them as run evidence.
  - Acceptance criteria:
    - workflow uploads manifest and at least one processed report as artifact
    - workflow names artifacts with commit SHA or run identifier

### P1: Data Lifecycle Discipline

- [ ] Introduce dataset version metadata for raw inputs.
  - Why: input fingerprint is good, but explicit dataset versioning makes the lineage story much stronger.
  - Acceptance criteria:
    - pipeline writes raw dataset metadata artifact
    - metadata includes source path, row counts, schema columns and fingerprint
    - manifest references that metadata

- [ ] Support explicit backfill window parameters in the official CLI.
  - Why: “reprocessable” is stronger when the pipeline exposes a formal re-run window instead of only whole-dataset reruns.
  - Acceptance criteria:
    - CLI accepts a bounded processing window or as-of date
    - outputs record the selected window in manifest
    - tests cover deterministic rerun with the same window

- [ ] Upgrade freshness checks from file-age only to source-aware metadata.
  - Why: file mtime is acceptable as a lightweight baseline, but it is still operationally weak.
  - Acceptance criteria:
    - freshness artifact includes source timestamps or declared extraction timestamp
    - stale condition references source metadata instead of only filesystem metadata

### P1: Governance and Contracts

- [ ] Extend contracts to one upstream interface that materially matters.
  - Why: currently contracts focus on curated outputs; adding one upstream contract improves confidence without over-modeling the whole repo.
  - Candidate scope:
    - silver customers
    - silver orders
    - API score payload examples
  - Acceptance criteria:
    - one additional contract is enforced in code
    - data dictionary reflects the expanded governed surface

- [ ] Add contract drift detection test for governed outputs.
  - Why: recruiters and reviewers notice when contracts exist but are not defended.
  - Acceptance criteria:
    - test fails on unexpected column additions/removals in governed outputs

### P2: Platform Hardening

- [ ] Add warehouse target abstraction tests for a second target path.
  - Why: not necessarily full production support, but evidence that the design can evolve without collapsing into SQLite-only assumptions.
  - Acceptance criteria:
    - second persistence path is validated at least at configuration and failure-handling level
    - docs clearly state supported vs experimental targets

- [ ] Tighten package boundaries between pipeline core and optional surfaces.
  - Why: Streamlit, API, dbt and orchestration examples should remain consumers of the batch core, not alternate centers of gravity.
  - Acceptance criteria:
    - batch pipeline remains the single authoritative operating path
    - optional interfaces do not duplicate orchestration logic

- [ ] Add a minimal changelog/release discipline for operational changes.
  - Why: small repos benefit from explicit release notes when they claim production-minded operation.
  - Acceptance criteria:
    - release notes summarize operational changes and breaking changes
    - README links to real release notes only

## Explicit Non-Goals

- do not add Spark, Kafka, Airflow-first orchestration or cloud services just for optics
- do not create fake medallion complexity beyond what the repository uses
- do not add observability vendors, secrets managers or infra modules without a real execution path
- do not replace simple file-based governance with heavyweight catalog tooling

## Proposed Execution Order

1. Container smoke test with artifact assertions
2. SQLite integration validation
3. Raw dataset metadata and source-aware freshness
4. Backfill window support in CLI and manifests
5. One additional governed contract
6. Package boundary cleanup and release discipline

## Definition of Done

- all new behavior is covered by automated tests
- CI validates the new behavior end to end
- README and architecture docs are updated only where behavior actually changed
- no new aspirational claims are introduced
- the project remains small, understandable, and runnable locally

## Reviewer Standard

If a staff engineer or hiring reviewer reads this repository after this issue is complete, the expected conclusion should be:

`This is still a compact portfolio project, but it is engineered with real discipline, clear operational intent, and credible trade-off management.`
