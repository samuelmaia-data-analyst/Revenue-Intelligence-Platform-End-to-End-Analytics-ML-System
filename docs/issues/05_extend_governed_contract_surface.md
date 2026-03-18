# Issue 05: Extend Governance to One Upstream Contract Surface

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

- one additional contract surface is enforced in code
- tests fail on breaking schema drift
- docs state exactly which surfaces are governed

## Non-Goals

- no contract explosion
- no attempt to model every internal dataframe

## Done When

- governance coverage expands in a way that is technically defensible and maintainable

