# Issue 01: Add Container Smoke Test and Publish Run Artifacts

## Goal

Prove that the official container image executes the batch pipeline successfully and expose the resulting artifacts in CI.

## Why

Docker build success alone is weak evidence. The stronger signal is showing that the built image can run the official CLI and produce the expected operational outputs.

## Scope

- execute `python -m src.pipeline run` inside the main image in CI
- assert presence of core output artifacts after container execution
- upload manifest and selected processed reports as GitHub Actions artifacts

## Acceptance Criteria

- CI runs the main image and executes the official pipeline command
- workflow fails if core artifacts are missing
- workflow uploads at least:
  - `pipeline_manifest.json`
  - `quality_report.json`
  - `kpi_snapshot.json`
- artifact names include run context such as commit SHA or workflow run ID

## Non-Goals

- no deployment workflow
- no registry publish workflow
- no orchestration platform integration

## Done When

- the repository proves batch execution inside the container, not just image construction

