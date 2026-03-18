# Contributing

## Working Standard

Treat this repository as a small production-minded system.

That means:

- optimize for clarity, reliability, and reproducibility
- prefer removing ambiguity over adding features
- keep documentation faithful to the implemented system
- do not add enterprise-style complexity unless the repository can justify it

## Before You Change Code

Read these files first:

- [README.md](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/README.md)
- [docs/architecture.md](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/docs/architecture.md)
- [docs/repository_structure.md](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/docs/repository_structure.md)

## Contribution Principles

- one official execution path: `python -m src.pipeline run`
- optional interfaces must not become alternate orchestration centers
- every meaningful change should reduce risk, improve maintainability, or strengthen operational credibility
- avoid decorative refactors with no measurable benefit

## Change Categories

### Acceptable high-signal changes

- reliability hardening
- clearer contracts and validation
- deterministic batch behavior
- operational visibility and traceability
- test coverage for important failure modes
- documentation aligned with implemented behavior

### Low-signal changes to avoid

- speculative abstractions
- framework churn without operational payoff
- broad renames with no architectural value
- aspirational docs for behavior that does not exist

## Local Workflow

Setup:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env
```

Run the official pipeline:

```powershell
python -m src.pipeline run
```

Generate governance artifacts only:

```powershell
python -m src.pipeline artifacts
```

## Validation Expectations

Run before opening a PR:

```powershell
python -m ruff check .
python -m black --check .
python -m isort --check-only .
python -m mypy src services contracts main.py
python -m pytest -q
python -m build
```

If your change affects the container path, also validate:

```powershell
docker build -t revenue-intelligence .
docker run --rm revenue-intelligence
```

## Repository Boundaries

Use these rules when placing new code:

- `src/`: pipeline and domain logic
- `services/`: runtime service interfaces
- `contracts/`: governed schemas and compatibility shims
- `tests/`: behavioral and regression coverage
- `docs/`: documentation for real repository behavior

Compatibility shims exist. Prefer current versioned paths over legacy wrappers:

- import contracts from `contracts.v1.data_contract`
- use `services.api` as the API entrypoint

## Testing Standard

Add tests when changing:

- pipeline orchestration
- manifests or snapshots
- config resolution
- warehouse persistence
- governed schemas
- CLI behavior
- failure handling

If no test was added, the PR should explain why the existing coverage is sufficient.

## Documentation Standard

Update docs when behavior changes.

At minimum, review:

- `README.md`
- `README.pt-BR.md`
- `docs/architecture.md`
- `docs/repository_structure.md`

Do not document planned behavior as if it already exists.

## Pull Requests

Use the PR template in:

- [.github/pull_request_template.md](/C:/Users/samue/PycharmProjects/Revenue-Intelligence-Platform-End-to-End-Analytics-ML-System/.github/pull_request_template.md)

PRs should stay focused. If a change mixes reliability, UI, governance, and refactoring without a coherent reason, split it.

## Review Bar

A change is not ready if:

- it adds complexity without a clear operational payoff
- it weakens the batch core as the system’s center of gravity
- it introduces undocumented runtime behavior
- it changes outputs without corresponding validation
- it makes the README less honest
