from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_dbt_profile_is_environment_aware() -> None:
    profile_text = (PROJECT_ROOT / "dbt" / "profiles" / "profiles.yml.example").read_text(
        encoding="utf-8"
    )
    assert "env_var('DBT_TARGET'" in profile_text
    assert "postgres:" in profile_text
    assert "DBT_POSTGRES_HOST" in profile_text


def test_dbt_docs_workflow_builds_documented_models() -> None:
    workflow_text = (PROJECT_ROOT / ".github" / "workflows" / "dbt-docs.yml").read_text(
        encoding="utf-8"
    )
    assert "dbt --project-dir dbt build" in workflow_text
    assert "DBT_TARGET: ci" in workflow_text


def test_dbt_sources_scope_freshness_to_loaded_source() -> None:
    sources_text = (PROJECT_ROOT / "dbt" / "models" / "sources.yml").read_text(encoding="utf-8")
    assert "loaded_at_field: as_of_date" in sources_text
    assert "warn_after: {count: 12, period: hour}" in sources_text
    assert "error_after: {count: 24, period: hour}" in sources_text


def test_core_ci_runs_dbt_sqlite_smoke_validation() -> None:
    workflow_text = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "dbt-core dbt-sqlite" in workflow_text
    assert "python scripts/smoke_dbt_sqlite.py" in workflow_text
