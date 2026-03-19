from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_repository_contains_high_signal_operational_docs() -> None:
    expected_paths = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "README.pt-BR.md",
        PROJECT_ROOT / "README.pt-PT.md",
        PROJECT_ROOT / "CONTRIBUTING.md",
        PROJECT_ROOT / "CHANGELOG.md",
        PROJECT_ROOT / "docs" / "architecture.md",
        PROJECT_ROOT / "docs" / "runtime_surfaces.md",
        PROJECT_ROOT / "docs" / "environments.md",
        PROJECT_ROOT / "docs" / "runbook.md",
        PROJECT_ROOT / "docs" / "incident_playbooks.md",
        PROJECT_ROOT / "docs" / "troubleshooting_matrix.md",
        PROJECT_ROOT / "docs" / "release_process.md",
        PROJECT_ROOT / "docs" / "deprecation_policy.md",
        PROJECT_ROOT / "docs" / "merge_policy.md",
        PROJECT_ROOT / "docs" / "sql_examples.md",
        PROJECT_ROOT / "docs" / "hiring_review.md",
        PROJECT_ROOT / "docs" / "releases" / "v1.1.0.md",
        PROJECT_ROOT / "docs" / "releases" / "v1.2.0.md",
        PROJECT_ROOT / "docs" / "releases" / "v1.3.0.md",
        PROJECT_ROOT / "docs" / "releases" / "v1.3.1.md",
        PROJECT_ROOT / "docs" / "releases" / "v1.3.2.md",
    ]
    for path in expected_paths:
        assert path.exists(), f"Missing governance or documentation asset: {path}"


def test_ci_workflow_enforces_core_quality_gates() -> None:
    workflow_text = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    for expected_snippet in [
        "python -m ruff check .",
        "python -m black --check .",
        "python -m isort --check-only .",
        "python -m pytest -q",
        "python scripts/smoke_dashboard.py",
        "python scripts/ui_snapshot.py",
        "python scripts/smoke_api.py",
        "python scripts/smoke_downstream_sql.py",
        "python scripts/smoke_processed_exports.py",
        "python scripts/smoke_partner_payload.py",
        "python scripts/smoke_dbt_sqlite.py",
        "API container smoke test",
        "http://127.0.0.1:8000/health",
        "python -m build",
    ]:
        assert expected_snippet in workflow_text


def test_pr_template_and_makefile_expose_senior_review_workflow() -> None:
    pr_template = (PROJECT_ROOT / ".github" / "pull_request_template.md").read_text(
        encoding="utf-8"
    )
    makefile_text = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")

    for expected_snippet in [
        "Official batch path affected",
        "Contracts affected",
        "Residual risks",
        "Rollback path",
    ]:
        assert expected_snippet in pr_template

    for expected_target in [
        "help:",
        "smoke-dashboard:",
        "snapshot-dashboard:",
        "smoke-api:",
        "smoke-downstream:",
        "smoke-exports:",
        "smoke-partner:",
        "smoke-dbt:",
        "verify:",
        "clean:",
    ]:
        assert expected_target in makefile_text


def test_readme_and_docs_map_reference_core_operational_docs() -> None:
    readme_text = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    docs_map_text = (PROJECT_ROOT / "docs" / "README.md").read_text(encoding="utf-8")

    shared_references = [
        "docs/architecture.md",
        "docs/runtime_surfaces.md",
        "docs/environments.md",
        "docs/runbook.md",
        "docs/troubleshooting_matrix.md",
        "docs/release_process.md",
        "docs/deprecation_policy.md",
        "docs/merge_policy.md",
        "docs/sql_examples.md",
        "docs/incident_playbooks.md",
        "docs/hiring_review.md",
    ]
    for reference in shared_references:
        assert reference in readme_text
        assert reference.replace("docs/", "") in docs_map_text or reference in docs_map_text
