# Troubleshooting Matrix

This matrix is meant to shorten time-to-diagnosis. Use it before debugging code blindly.

| Symptom | Likely Layer | First Artifact to Inspect | Typical Cause | First Action |
| --- | --- | --- | --- | --- |
| Pipeline fails before reporting | silver validation | `quality_report.json` or failure manifest | missing required columns, bad types, duplicated keys | inspect raw inputs and silver validation assumptions |
| Pipeline fails after reporting starts | processed artifact validation | `artifact_validation_report.json` or failure manifest | schema drift in curated CSV/JSON outputs | compare output shape with `src/artifact_validation.py` and reporting code |
| Run succeeds but alerts are warnings | monitoring or quality | `alerts_report.json` | drift, calibration degradation, null growth or duplicates | inspect linked monitoring and quality artifacts before changing thresholds |
| Dashboard starts but shows empty state | filtered recommendations | `recommendations.csv` | valid run with no matching slice, stale outputs or aggressive filters | run dashboard smoke, inspect filters and recommendation volume |
| Dashboard import or load fails | app data access | processed JSON/CSV artifacts | missing processed files or corrupted artifact shape | run `python scripts/smoke_dashboard.py` and inspect latest pipeline outputs |
| Warehouse queries do not match processed artifacts | persistence | `pipeline_manifest.json` and warehouse file | warehouse stage failed or stale database inspected | confirm `warehouse.<target>` stage completed and rerun pipeline |
| Backfill run completes with unexpectedly low volume | backfill window | `pipeline_manifest.json` | overly restrictive date window or customer cutoff | inspect `backfill_window` in manifest and compare against source date range |
| Retry did not help | orchestration | failure manifest and run log | deterministic bug, not transient failure | fix stage logic or input assumptions instead of increasing retries |
| Smoke test passes locally but CI fails | environment parity | CI logs and `.env.example` | missing dependency, path difference or assumptions about local state | align config defaults and avoid hidden local dependencies |

## Escalation Rule

If the first artifact does not explain the failure, inspect in this order:

1. latest failure manifest
2. latest run log
3. processed validation artifacts
4. relevant stage implementation in `src/`

If those still do not explain the issue, add a regression test before changing behavior.
