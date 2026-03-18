# GitHub Issue Templates

Este arquivo consolida versões prontas para copiar e colar no GitHub.

## Issue 01

### Title

`[P0] Add container smoke test and publish run artifacts in CI`

### Labels

`priority:P0`, `type:operations`, `type:testing`

### Body

```md
## Goal

Prove that the official container image executes the batch pipeline successfully and expose the resulting run artifacts in CI.

## Why

Docker build success alone is weak evidence. The stronger signal is showing that the built image can run the official CLI and produce the expected operational outputs.

## Scope

- execute `python -m src.pipeline run` inside the main image in CI
- assert presence of core output artifacts after container execution
- upload manifest and selected processed reports as GitHub Actions artifacts

## Acceptance Criteria

- [ ] CI runs the main image and executes the official pipeline command
- [ ] workflow fails if core artifacts are missing
- [ ] workflow uploads at least:
  - [ ] `pipeline_manifest.json`
  - [ ] `quality_report.json`
  - [ ] `kpi_snapshot.json`
- [ ] artifact names include run context such as commit SHA or workflow run ID

## Non-Goals

- no deployment workflow
- no registry publish workflow
- no orchestration platform integration

## Done When

The repository proves batch execution inside the container, not just image construction.
```

---

## Issue 02

### Title

`[P0] Add SQLite warehouse integration validation`

### Labels

`priority:P0`, `type:testing`, `type:reliability`

### Body

```md
## Goal

Validate the warehouse as an actual analytical interface, not just as a generated file.

## Why

A SQLite database file existing on disk is not enough. The repository should prove that persisted tables are queryable and structurally coherent.

## Scope

- add integration tests that open the generated SQLite database
- validate required table presence
- validate non-zero row counts where appropriate
- validate at least one join path across curated tables

## Acceptance Criteria

- [ ] tests assert existence of the expected warehouse tables
- [ ] tests assert row counts for key tables such as:
  - [ ] `fact_orders`
  - [ ] `customer_features`
  - [ ] `recommendations`
- [ ] tests execute at least one SQL join demonstrating analytical interoperability

## Non-Goals

- no migration framework
- no warehouse abstraction rewrite
- no heavy ORM layer

## Done When

The warehouse is defended as a real downstream interface.
```

---

## Issue 03

### Title

`[P1] Add raw dataset metadata and source-aware freshness`

### Labels

`priority:P1`, `type:governance`, `type:operations`

### Body

```md
## Goal

Upgrade lineage and freshness from filesystem-level heuristics to source-aware metadata.

## Why

The current input fingerprint and file-age checks are useful, but still lightweight. A stronger operational story requires explicit raw dataset metadata recorded as part of each run.

## Scope

- write raw dataset metadata artifact
- include source file names, row counts, schema columns and dataset fingerprint
- update freshness report to reference source metadata timestamps when available
- link raw metadata from the run manifest

## Acceptance Criteria

- [ ] pipeline generates a raw metadata artifact in processed or manifest scope
- [ ] manifest references raw metadata location or embeds key summary fields
- [ ] freshness artifact distinguishes source timestamp from filesystem mtime where possible
- [ ] tests cover metadata creation and freshness evaluation

## Non-Goals

- no external metadata platform
- no data catalog integration

## Done When

Reviewers can trace what raw dataset version fed a given run.
```

---

## Issue 04

### Title

`[P1] Support explicit backfill window in the official CLI`

### Labels

`priority:P1`, `type:architecture`, `type:operations`

### Body

```md
## Goal

Make reprocessing more explicit by supporting a formal processing window or `as_of_date` in the official CLI.

## Why

A production-minded batch system should expose bounded reruns instead of relying only on full dataset refreshes.

## Scope

- add CLI parameters for processing window or explicit `as_of_date`
- record selected window in the run manifest
- ensure rerunning the same window remains deterministic

## Acceptance Criteria

- [ ] CLI accepts explicit bounded reprocessing parameters
- [ ] manifest records the selected processing window
- [ ] tests prove deterministic reruns with the same window
- [ ] docs describe the new official usage clearly and honestly

## Non-Goals

- no scheduler-specific backfill implementation
- no partition orchestration framework

## Done When

The pipeline supports a defensible backfill story.
```

---

## Issue 05

### Title

`[P1] Extend governance to one upstream contract surface`

### Labels

`priority:P1`, `type:governance`, `type:testing`

### Body

```md
## Goal

Expand governance beyond gold outputs in one high-value place without over-modeling the repository.

## Why

Current governance is useful, but concentrated on curated outputs. Adding one upstream contract increases engineering credibility while keeping maintenance proportional.

## Candidate Targets

- silver customers
- silver orders
- API score payload examples

## Scope

- choose one target surface
- define and enforce a contract
- include it in generated governance documentation if appropriate
- add tests for drift or contract breakage

## Acceptance Criteria

- [ ] one additional contract surface is enforced in code
- [ ] tests fail on breaking schema drift
- [ ] docs state exactly which surfaces are governed

## Non-Goals

- no contract explosion
- no attempt to model every internal dataframe

## Done When

Governance coverage expands in a way that is technically defensible and maintainable.
```

---

## Issue 06

### Title

`[P2] Tighten package boundaries around the batch core`

### Labels

`priority:P2`, `type:architecture`

### Body

```md
## Goal

Ensure the batch pipeline remains the single authoritative operating path while optional surfaces stay as consumers.

## Why

Portfolio repositories often degrade when API, dashboard and orchestration examples start to duplicate pipeline logic or become competing entrypoints.

## Scope

- audit API, Streamlit, dbt and orchestration wrappers
- remove or reduce duplicated orchestration logic
- make the batch core the only source of truth for pipeline execution

## Acceptance Criteria

- [ ] optional surfaces delegate to the same underlying batch core where appropriate
- [ ] no duplicate orchestration flow remains without explicit justification
- [ ] docs clearly identify batch as the primary operating mode

## Non-Goals

- no rewrite of app or API feature sets
- no removal of optional interfaces unless they materially conflict with architecture

## Done When

The repository has one architectural center of gravity.
```

---

## Issue 07

### Title

`[P2] Add release discipline for operational changes`

### Labels

`priority:P2`, `type:documentation`, `type:operations`

### Body

```md
## Goal

Introduce a lightweight but credible release discipline for operationally meaningful changes.

## Why

If the repository claims production-minded operation, changes to manifests, retention, contracts and execution semantics should have explicit release notes.

## Scope

- define a lightweight release note format
- link release notes from the main README only when real entries exist
- document operationally relevant changes and breaking behavior

## Acceptance Criteria

- [ ] at least one new release note entry documents recent operational hardening
- [ ] release notes distinguish:
  - [ ] added
  - [ ] changed
  - [ ] fixed
  - [ ] breaking, if applicable
- [ ] README references only implemented and published release notes

## Non-Goals

- no semantic-release automation
- no versioning ceremony beyond what this repository can sustain

## Done When

Operational evolution is recorded with discipline instead of implicit repo drift.
```
