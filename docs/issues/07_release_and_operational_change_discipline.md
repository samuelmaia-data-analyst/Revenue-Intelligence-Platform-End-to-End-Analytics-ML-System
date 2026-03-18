# Issue 07: Add Release Discipline for Operational Changes

## Goal

Introduce a lightweight but credible release discipline for operationally meaningful changes.

## Why

If the repository claims production-minded operation, changes to manifests, retention, contracts and execution semantics should have explicit release notes.

## Scope

- define a lightweight release note format
- link release notes from the main README only when real entries exist
- document operationally relevant changes and breaking behavior

## Acceptance Criteria

- at least one new release note entry documents recent operational hardening
- release notes distinguish:
  - added
  - changed
  - fixed
  - breaking, if applicable
- README references only implemented and published release notes

## Non-Goals

- no semantic-release automation
- no versioning ceremony beyond what this repository can sustain

## Done When

- operational evolution is recorded with discipline instead of implicit repo drift

