# Compatibility and Deprecation Policy

## Purpose

This repository contains a small number of compatibility shims to preserve stable import paths while the project evolves.

These shims exist for practical migration support, not as permanent architectural layers.

## Current Compatibility Paths

Current examples:

- `api/`
- `contracts/data_contract.py`
- `src/data_contract.py`

Canonical paths should be preferred in new code:

- `services.api`
- `contracts.v1.data_contract`

## Deprecation Rule

When a compatibility path exists:

1. document the canonical path
2. keep the shim narrow and obvious
3. avoid building new features on the shim path
4. record breaking changes in release notes and changelog

## When to Remove a Shim

A shim is a candidate for removal when:

- all internal imports already use the canonical path
- the compatibility layer no longer protects a meaningful migration path
- removal improves clarity without breaking the hiring value of the repository

## Repository Guidance

For this project, compatibility should always serve clarity.

If a shim starts to confuse reviewers more than it helps backwards compatibility, it should be scheduled for removal in a future release note and changelog entry.
