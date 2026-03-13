from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_scheduler_examples_exist() -> None:
    expected = [
        PROJECT_ROOT / "orchestration" / "README.md",
        PROJECT_ROOT / "orchestration" / "airflow" / "dags" / "revenue_intelligence_platform_dag.py",
        PROJECT_ROOT / "orchestration" / "prefect" / "revenue_intelligence_deployment.yaml",
        PROJECT_ROOT / ".github" / "workflows" / "dbt-docs.yml",
    ]
    for path in expected:
        assert path.exists(), f"Missing operational asset: {path}"


def test_dbt_governance_assets_exist() -> None:
    expected = [
        PROJECT_ROOT / "dbt" / "models" / "exposures.yml",
        PROJECT_ROOT / "dbt" / "models" / "sources.yml",
    ]
    for path in expected:
        assert path.exists(), f"Missing dbt governance asset: {path}"
