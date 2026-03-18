# Project Board: Staff Upgrade Execution Plan

## Board Purpose

Turn the upgrade backlog into an execution sequence that is easy to run, review and track.

This board assumes the master issue is the umbrella and each child issue is delivered independently with tests and documentation updates.

## Suggested Labels

- `priority:P0`
- `priority:P1`
- `priority:P2`
- `type:reliability`
- `type:governance`
- `type:operations`
- `type:testing`
- `type:architecture`
- `type:documentation`
- `status:blocked`
- `status:ready`
- `status:in-progress`
- `status:review`

## Suggested Columns

- `Backlog`
- `Ready`
- `In Progress`
- `Review`
- `Done`

## Execution Table

| Order | Issue | Priority | Est. | Depends On | Suggested Labels | Definition of Ready |
|---|---|---|---:|---|---|---|
| 1 | [01 Container Smoke and CI Artifacts](./01_container_smoke_and_ci_artifacts.md) | P0 | 0.5-1d | None | `priority:P0`, `type:operations`, `type:testing` | CI workflow structure understood and Docker path stable |
| 2 | [02 SQLite Integration Validation](./02_sqlite_integration_validation.md) | P0 | 0.5-1d | None | `priority:P0`, `type:testing`, `type:reliability` | Core warehouse tables and current schema are stable |
| 3 | [03 Raw Dataset Metadata and Freshness](./03_raw_dataset_metadata_and_freshness.md) | P1 | 1-1.5d | 01 | `priority:P1`, `type:governance`, `type:operations` | Current manifest/freshness model is accepted as baseline |
| 4 | [04 Backfill Window CLI](./04_backfill_window_cli.md) | P1 | 1-1.5d | 03 | `priority:P1`, `type:architecture`, `type:operations` | Raw metadata and run manifest structure are stable enough to extend |
| 5 | [05 Extend Governed Contract Surface](./05_extend_governed_contract_surface.md) | P1 | 0.5-1d | 03 | `priority:P1`, `type:governance`, `type:testing` | Target contract surface is explicitly chosen |
| 6 | [06 Package Boundary Cleanup](./06_package_boundary_cleanup.md) | P2 | 1d | 01, 04 | `priority:P2`, `type:architecture` | Batch core behavior and CLI semantics are settled |
| 7 | [07 Release and Operational Change Discipline](./07_release_and_operational_change_discipline.md) | P2 | 0.5d | 01-06 | `priority:P2`, `type:documentation`, `type:operations` | Enough implemented change exists to justify release notes |

## Dependency View

### Critical Path

1. Issue 01
2. Issue 03
3. Issue 04
4. Issue 06
5. Issue 07

### Parallelizable Work

- Issue 01 and Issue 02 can run in parallel
- Issue 05 can start after Issue 03 without waiting for Issue 04

## Delivery Standard Per Issue

Every issue should include:

- code changes only where operational value is clear
- automated tests for the new behavior
- no aspirational README claims
- explicit update to docs if runtime behavior changes
- no duplicate execution path outside the official CLI unless justified

## Review Checklist

- Does this change reduce risk or ambiguity?
- Does it strengthen reproducibility or traceability?
- Is the new behavior observable through tests or CI artifacts?
- Is the complexity proportional to the repository size?
- Would a staff engineer consider this change disciplined rather than decorative?

## Recommended Milestones

### Milestone 1: Operational Proof

- Issue 01
- Issue 02

Outcome:
- the repo proves that the official container and warehouse path actually work

### Milestone 2: Stronger Data Lifecycle

- Issue 03
- Issue 04
- Issue 05

Outcome:
- the repo tells a stronger lineage, freshness and reprocessing story

### Milestone 3: Architectural Polish

- Issue 06
- Issue 07

Outcome:
- the repo presents one coherent center of gravity with disciplined release communication

## Definition of Program Done

- all child issues are completed
- CI proves both code quality and operational execution
- manifests, metadata and contracts remain faithful to code
- the repository still feels compact, not bloated
- the resulting project reads as intentionally engineered rather than embellished
