# Issue 02: Add SQLite Warehouse Integration Validation

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

- tests assert existence of the expected warehouse tables
- tests assert row counts for key tables such as:
  - `fact_orders`
  - `customer_features`
  - `recommendations`
- tests execute at least one SQL join demonstrating analytical interoperability

## Non-Goals

- no migration framework
- no warehouse abstraction rewrite
- no heavy ORM layer

## Done When

- the warehouse is defended as a real downstream interface

