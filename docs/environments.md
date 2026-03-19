# Environment Model

This repository intentionally keeps the environment story small and explicit.

## Supported Environments

### Local application environment

Purpose:
- run the batch pipeline
- run tests
- run Streamlit
- run the API smoke

Interpreter:
- `.venv\Scripts\python.exe`

Packages:
- `requirements.txt`
- `requirements-dev.txt`

### Local dbt CLI environment

Purpose:
- run `dbt` without destabilizing the application environment

Interpreter:
- `.dbt-venv\Scripts\python.exe`

Packages:
- `dbt-core`
- `dbt-sqlite`

Rule:
- do not install `dbt` into `.venv`

### CI environment

Purpose:
- prove that lint, tests, smokes, build, dbt validation, and container paths still work

Owner:
- `.github/workflows/ci.yml`

## Environment Rules

1. `.venv` is the default runtime for application code.
2. `.dbt-venv` exists only to isolate the `dbt` CLI.
3. CI is the canonical reference for what must stay green.
4. Local success is not enough if CI does not validate the same surface.

## Typical Commands

Application runtime:

```powershell
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe scripts\smoke_dashboard.py
.venv\Scripts\python.exe scripts\smoke_api.py
```

dbt runtime:

```powershell
.venv\Scripts\python.exe scripts\smoke_dbt_sqlite.py
.dbt-venv\Scripts\dbt.exe --project-dir dbt run
```

## Drift Prevention

If a command succeeds only outside `.venv`, that is usually environment drift rather than a code fix.

If `dbt` requires a dependency change that breaks Streamlit or the API, fix the environment boundary first instead of weakening the application stack.
