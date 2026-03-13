from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_dbt_profile_is_environment_aware() -> None:
    profile_text = (
        PROJECT_ROOT / "dbt" / "profiles" / "profiles.yml.example"
    ).read_text(encoding="utf-8")
    assert "env_var('DBT_TARGET'" in profile_text
    assert "postgres:" in profile_text
    assert "DBT_POSTGRES_HOST" in profile_text


def test_dbt_docs_workflow_runs_freshness() -> None:
    workflow_text = (
        PROJECT_ROOT / ".github" / "workflows" / "dbt-docs.yml"
    ).read_text(encoding="utf-8")
    assert "dbt --project-dir dbt source freshness" in workflow_text
    assert "DBT_TARGET: ci" in workflow_text


def test_dbt_sources_define_freshness_sla() -> None:
    sources_text = (
        PROJECT_ROOT / "dbt" / "models" / "sources.yml"
    ).read_text(encoding="utf-8")
    assert "warn_after: {count: 12, period: hour}" in sources_text
    assert "error_after: {count: 24, period: hour}" in sources_text
