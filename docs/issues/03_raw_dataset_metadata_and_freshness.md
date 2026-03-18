# Issue 03: Add Raw Dataset Metadata and Source-Aware Freshness

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

- pipeline generates a raw metadata artifact in processed or manifest scope
- manifest references raw metadata location or embeds key summary fields
- freshness artifact distinguishes source timestamp from filesystem mtime where possible
- tests cover metadata creation and freshness evaluation

## Non-Goals

- no external metadata platform
- no data catalog integration

## Done When

- reviewers can trace what raw dataset version fed a given run

