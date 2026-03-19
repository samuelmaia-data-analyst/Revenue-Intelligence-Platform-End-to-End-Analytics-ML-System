# Contributing

## Principles

- Keep changes focused on one problem.
- Prefer fixing logic at the source over compensating downstream.
- Do not hide data quality or schema issues that should fail loudly.
- Preserve the public CLI unless the change explicitly requires a behavior update.

## Development workflow

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
pre-commit install
```

## Before opening a pull request

Run the narrowest checks that prove correctness, then broader checks when the change is cross-cutting:

```bash
make lint
make test
```

## Coding expectations

- Add type hints to new Python code.
- Keep pipeline steps readable and explicit.
- Prefer small helper functions over long multi-purpose functions.
- Use actionable exception messages tied to the failing dataset or stage.
- Document operator-visible behavior changes in `README.md`.

## Data engineering expectations

- Treat `README.md` as the operator-facing source of truth.
- Treat `pyproject.toml` as the source of truth for dependencies and entry points.
- Treat `Makefile` as the preferred shorthand for local quality commands.
- If a change alters schema or output artifact names, update tests and downstream consumers.

## Pull request expectations

- explain the engineering outcome clearly
- call out data, compatibility, or operational risk
- list the checks you ran
- update docs when behavior or architecture changed
