# Commit Convention

This repository uses Conventional Commits to make history readable and to separate behavior changes from maintenance work.

## Format

```text
type(scope): imperative summary
```

Scope is recommended when it improves clarity and should usually match a project area such as `pipelines`, `dashboard`, `models`, `analytics`, `docs`, `tests`, or `github`.

## Accepted Types

- `feat`
- `fix`
- `docs`
- `refactor`
- `test`
- `ci`
- `chore`

## Good Examples

```text
feat(analytics): add cohort retention summary output
fix(pipelines): fail loudly on missing customer id
docs(contributing): define PR validation expectations
ci(github): cache pip dependencies in CI
test(dashboard): cover demo-mode fallback behavior
```

## Poor Examples

```text
update readme
fix bug
changes
stuff
```

## Practical Rules

- One commit should communicate one coherent change.
- Separate docs-only or automation-only work when practical.
- Keep the subject line short enough to scan in `git log`.
- Use the body when the rationale, migration impact, or trade-off is not obvious.
- Mention schema, artifact, or operator impact in the body for pipeline-affecting changes.

## Suggested Commit Body Template

```text
<type>(<scope>): <summary>

Why:
- explain the problem or motivation

What:
- summarize the technical change

Validation:
- list the commands run
```
