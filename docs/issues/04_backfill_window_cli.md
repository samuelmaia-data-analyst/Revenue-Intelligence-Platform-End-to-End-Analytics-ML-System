# Issue 04: Support Explicit Backfill Window in the Official CLI

## Goal

Make reprocessing more explicit by supporting a formal processing window or `as_of_date` in the official CLI.

## Why

A production-minded batch system should expose bounded reruns instead of relying only on full dataset refreshes.

## Scope

- add CLI parameters for processing window or explicit `as_of_date`
- record selected window in the run manifest
- ensure rerunning the same window remains deterministic

## Acceptance Criteria

- CLI accepts explicit bounded reprocessing parameters
- manifest records the selected processing window
- tests prove deterministic reruns with the same window
- docs describe the new official usage clearly and honestly

## Non-Goals

- no scheduler-specific backfill implementation
- no partition orchestration framework

## Done When

- the pipeline supports a defensible backfill story

