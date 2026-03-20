# Contributing

This repository is maintained as a small but disciplined data platform. Contributions should improve the system without weakening pipeline safety, CLI ergonomics, testability, or dashboard operability.

## Working Principles

- Keep changes scoped to one engineering outcome.
- Fix problems at the source instead of layering compensating workarounds.
- Preserve explicit failure behavior for missing data, schema drift, and invalid operational states.
- Maintain existing CLI entry points unless the change intentionally updates the public surface.
- Treat documentation, tests, and automation as part of the change, not optional follow-up.

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
copy .env.example .env
pre-commit install
```

Preferred commands:

```bash
make install
make bootstrap
make pipeline
make health
make lint
make test
make build
make check
make format
make precommit
```

If your shell does not provide `make`, use the Python task runner instead:

```bash
python -m ridp.dev_tasks install
python -m ridp.dev_tasks lint
python -m ridp.dev_tasks test
python -m ridp.dev_tasks check
python -m ridp.dev_tasks dashboard
```

## Development Flow

1. Create a focused branch for the change.
2. Implement the smallest coherent change that solves the problem.
3. Add or update tests when behavior, contracts, or outputs change.
4. Update `README.md` for operator-visible setup or usage changes.
5. Update `docs/` when architecture, data flow, or assumptions change.
6. Run the narrowest checks that prove correctness, then broader checks for cross-cutting work.
7. Open a pull request with explicit impact, risk, and validation notes.

## Validation Expectations

Use the smallest relevant proof first:

- docs or template changes: review rendered Markdown or YAML for structure and clarity
- Python logic change in one module: `make test`
- linting or typing impact: `make lint`
- release-ready or cross-cutting change: `make check`

If you cannot run a required validation step, call that out explicitly in the pull request.

## Code Expectations

- Add type hints to new Python code.
- Keep functions cohesive and readable.
- Prefer deterministic transforms where practical.
- Raise actionable exceptions that identify the failing stage, artifact, or contract.
- Avoid new dependencies unless they are clearly justified.
- Preserve current naming and module structure unless a rename is necessary.

## Data Platform Expectations

- `README.md` is the operator-facing source of truth.
- `pyproject.toml` is the source of truth for Python version, dependencies, and CLI entry points.
- `Makefile` is the preferred shorthand for common local commands, with `ridp-dev` as the cross-platform Python fallback.
- Pipeline outputs and schema changes must be reflected in downstream code and tests.
- Do not silently swallow empty-data or missing-column conditions that should fail loudly.

## Dashboard Expectations

- Preserve compatibility with `ridp-dashboard`.
- Prefer graceful degradation only when artifacts are legitimately optional, such as demo-mode fallbacks.
- Do not hide actionable failures behind empty states if the operator needs to fix the environment.

## Commit Convention

This repository follows Conventional Commits with a pragmatic, engineering-first bias.

Format:

```text
type(scope): imperative summary
```

Examples:

- `feat(pipelines): add business KPI freshness metadata`
- `fix(dashboard): guard missing run history sidecars`
- `docs(readme): clarify local bootstrap flow`
- `ci(github): split lint and test jobs`
- `refactor(models): simplify churn feature assembly`
- `test(pipelines): cover invalid delivered timestamp`

Allowed primary types:

- `feat`: user-facing capability or meaningful platform enhancement
- `fix`: bug fix or regression correction
- `docs`: documentation-only change
- `refactor`: internal code change without intended behavior shift
- `test`: test-only addition or update
- `ci`: CI, workflow, hooks, or automation changes
- `chore`: maintenance that does not fit the categories above

Rules:

- Use the imperative mood.
- Keep the summary concise and specific.
- Include a scope when it improves clarity.
- Split unrelated work into separate commits.
- Avoid vague summaries such as `update files` or `fix stuff`.

See [docs/commit-convention.md](docs/commit-convention.md) for the full guide and examples.

## Pull Request Standard

A strong pull request in this repository:

- explains the engineering outcome clearly
- identifies behavioral, data, or operational risk
- states what was validated and what was not
- links issues or background context when relevant
- updates docs and tests when the change affects operators or downstream consumers

Use the PR template as a minimum bar, not a box-ticking exercise.

## Review Standard

Reviewers should prioritize:

- correctness and regression risk
- contract, schema, and artifact stability
- operational clarity and failure behavior
- test adequacy
- documentation completeness for operator-facing changes

## Release And Automation Notes

- Keep CI green before merging.
- Prefer fixing local hook or CI failures rather than bypassing them.
- If automation changes alter the developer workflow, document the impact in `README.md` or this file.
