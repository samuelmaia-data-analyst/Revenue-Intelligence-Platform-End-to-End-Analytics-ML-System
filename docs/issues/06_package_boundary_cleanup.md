# Issue 06: Tighten Package Boundaries Around the Batch Core

## Goal

Ensure the batch pipeline remains the single authoritative operating path while optional surfaces stay as consumers.

## Why

Portfolio repositories often degrade when API, dashboard and orchestration examples start to duplicate pipeline logic or become competing entrypoints.

## Scope

- audit API, Streamlit, dbt and orchestration wrappers
- remove or reduce duplicated orchestration logic
- make the batch core the only source of truth for pipeline execution

## Acceptance Criteria

- optional surfaces delegate to the same underlying batch core where appropriate
- no duplicate orchestration flow remains without explicit justification
- docs clearly identify batch as the primary operating mode

## Non-Goals

- no rewrite of app or API feature sets
- no removal of optional interfaces unless they materially conflict with architecture

## Done When

- the repository has one architectural center of gravity

