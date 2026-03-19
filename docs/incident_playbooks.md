# Incident Playbooks

This document complements the runbook. Use it when the failure class is already known and you need the shortest credible containment path.

## Playbook: Processed Artifact Drift

Trigger:
- `artifact_validation_report.json` fails
- processed export smoke fails

Immediate actions:
1. identify the first missing or invalid artifact
2. compare it against `src/artifact_validation.py`
3. inspect the reporting stage that produced it
4. add or update a regression test before changing the contract

Do not:
- silently relax the contract
- reclassify a breaking change as a documentation fix

Example:
- `top_10_actions.csv` no longer matches `business_outcomes.json`

## Playbook: Warehouse and dbt Divergence

Trigger:
- downstream SQL smoke fails
- `dbt` smoke fails after a successful pipeline run

Immediate actions:
1. confirm `warehouse.<target>` succeeded in `pipeline_manifest.json`
2. inspect `data/warehouse/revenue_intelligence.db`
3. inspect `dbt/target/run_results.json`
4. identify whether the issue is warehouse persistence or dbt model logic

Do not:
- patch dbt models to fit stale warehouse state
- skip the smoke to get CI green

Example:
- `dbt` smoke starts failing after a warehouse column rename

## Playbook: API Container Unhealthy

Trigger:
- API container smoke does not reach `/health`
- local API smoke passes but Docker path fails

Immediate actions:
1. inspect Docker logs
2. verify `RIP_MODEL_DIR` resolution inside the container
3. confirm models are present in the expected processed registry layout
4. rerun `scripts/smoke_api.py` locally before changing the image

Do not:
- weaken the health endpoint contract
- bypass model loading to make the container look healthy

Example:
- container boots but `/health` never stabilizes because the model registry path moved

## Playbook: Dashboard Looks Correct but Business Slice Is Wrong

Trigger:
- Streamlit app loads
- users report wrong ranking or empty high-value segments

Immediate actions:
1. inspect `recommendations.csv`
2. inspect `top_10_actions.csv`
3. run `scripts/smoke_dashboard.py`
4. compare the selected filters with the processed export volume

Do not:
- move core ranking logic into the dashboard
- add UI-only corrections that diverge from processed outputs

Example:
- the dashboard ranking differs from `top_10_actions.csv` after a UI-only filter change

## Playbook: Environment Drift

Trigger:
- local validation diverges from CI
- dashboard or API smokes fail after dependency changes

Immediate actions:
1. confirm `.venv` is used for app and test runtime
2. confirm `.dbt-venv` is used only for `dbt` CLI
3. run `pip check` in `.venv`
4. rerun the relevant smoke instead of trusting installation success

Do not:
- install `dbt` into `.venv`
- use local caches as evidence that the environment is healthy

Example:
- local `dbt` starts working, but Streamlit breaks because `protobuf` was upgraded in `.venv`
