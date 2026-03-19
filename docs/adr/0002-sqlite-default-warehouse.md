# ADR 0002: SQLite Is the Default Warehouse

## Status

Accepted

## Context

The repository needs a warehouse target that:

- works locally without external infrastructure
- is easy for reviewers to run
- supports SQL validation and downstream consumption

Using a remote warehouse by default would add setup friction and make portfolio evaluation harder.

## Decision

SQLite is the default warehouse target for local execution and CI smoke validation.

The repository keeps compatibility points for other targets, but local reproducibility wins by default.

## Consequences

Positive:

- zero external dependency for default execution
- easy smoke testing in CI
- clear warehouse evidence for recruiters and reviewers

Negative:

- not representative of large-scale production concurrency
- some warehouse-specific optimization concerns remain out of scope

## Why This Is Worth It

This trade-off keeps the project honest. It demonstrates analytics engineering and operational discipline without hiding behind infrastructure complexity.
