from __future__ import annotations

import json
import os
import sqlite3
import sys
from dataclasses import replace
from pathlib import Path

import pandas as pd
import pytest

from src.config import PipelineConfig
from src.exceptions import PipelineStageError
from src.governance import build_data_dictionary
from src.orchestration import _apply_retention, run_pipeline
from src.pipeline import main as pipeline_main


def _build_config(tmp_path: Path, *, semantic_metrics_exists: bool = True) -> PipelineConfig:
    data_dir = tmp_path / "data"
    metrics_path = tmp_path / "metrics" / "semantic_metrics.json"
    if semantic_metrics_exists:
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        metrics_path.write_text(
            json.dumps(
                {
                    "version": "1.0",
                    "metrics": [{"name": "revenue_proxy", "expression": "sum(monetary)"}],
                }
            ),
            encoding="utf-8",
        )

    return PipelineConfig(
        project_root=tmp_path,
        data_dir=data_dir,
        raw_dir=data_dir / "raw",
        bronze_dir=data_dir / "bronze",
        silver_dir=data_dir / "silver",
        gold_dir=data_dir / "gold",
        processed_dir=data_dir / "processed",
        warehouse_dir=data_dir / "warehouse",
        warehouse_db_path=data_dir / "warehouse" / "revenue_intelligence.db",
        semantic_metrics_path=metrics_path,
        alerts_output_path=data_dir / "processed" / "alerts_report.json",
        approvals_output_path=data_dir / "processed" / "approved_actions.csv",
        runs_dir=data_dir / "runs",
        manifests_dir=data_dir / "manifests",
        snapshots_dir=data_dir / "snapshots",
        data_dictionary_path=data_dir / "processed" / "data_dictionary.json",
        env_name="test",
        warehouse_target="sqlite",
        warehouse_url=None,
        seed=42,
        log_level="WARNING",
        freshness_max_age_hours=48,
        snapshot_retention_runs=2,
        snapshot_retention_days=30,
        failure_retention_days=14,
    )


def test_pipeline_manifest_and_snapshot_are_created(tmp_path: Path) -> None:
    cfg = _build_config(tmp_path)

    manifest = run_pipeline(cfg)

    assert manifest["status"] == "success"
    assert manifest["run_id"]
    assert manifest["input_fingerprint"]
    assert (cfg.processed_dir / "pipeline_manifest.json").exists()
    assert len(list(cfg.snapshots_dir.iterdir())) == 1
    snapshot_dir = next(cfg.snapshots_dir.iterdir())
    assert (snapshot_dir / "processed" / "quality_report.json").exists()
    assert (snapshot_dir / "processed" / "kpi_snapshot.json").exists()
    assert (snapshot_dir / "processed" / "raw_input_metadata.json").exists()
    assert (snapshot_dir / cfg.warehouse_db_path.name).exists()


def test_pipeline_generates_raw_input_metadata_and_source_aware_freshness(tmp_path: Path) -> None:
    cfg = _build_config(tmp_path)

    run_pipeline(cfg)

    raw_metadata = json.loads(
        (cfg.processed_dir / "raw_input_metadata.json").read_text(encoding="utf-8")
    )
    freshness = json.loads(
        (cfg.processed_dir / "freshness_report.json").read_text(encoding="utf-8")
    )

    assert raw_metadata["dataset_count"] == 3
    assert {item["dataset_name"] for item in raw_metadata["datasets"]} == {
        "customers",
        "orders",
        "marketing_spend",
    }
    assert all(item["row_count"] > 0 for item in raw_metadata["datasets"])
    assert all("source_updated_at_utc" in item for item in raw_metadata["datasets"])
    assert all("fingerprint" in item for item in freshness["checks"])
    assert all("source_updated_at_utc" in item for item in freshness["checks"])


def test_pipeline_persists_queryable_sqlite_warehouse(tmp_path: Path) -> None:
    cfg = _build_config(tmp_path)

    run_pipeline(cfg)

    with sqlite3.connect(cfg.warehouse_db_path) as connection:
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name",
            connection,
        )
        joined = pd.read_sql_query(
            """
            SELECT COUNT(*) AS joined_rows
            FROM fact_orders fo
            INNER JOIN dim_customers dc ON fo.customer_id = dc.customer_id
            INNER JOIN recommendations r ON fo.customer_id = r.customer_id
            """,
            connection,
        )
        counts = pd.read_sql_query(
            """
            SELECT
                (SELECT COUNT(*) FROM fact_orders) AS fact_orders_count,
                (SELECT COUNT(*) FROM customer_features) AS customer_features_count,
                (SELECT COUNT(*) FROM recommendations) AS recommendations_count
            """,
            connection,
        )

    assert {"customer_features", "dim_customers", "fact_orders", "recommendations"}.issubset(
        set(tables["name"])
    )
    assert int(counts.loc[0, "fact_orders_count"]) > 0
    assert int(counts.loc[0, "customer_features_count"]) > 0
    assert int(counts.loc[0, "recommendations_count"]) > 0
    assert int(joined.loc[0, "joined_rows"]) > 0


def test_pipeline_is_idempotent_for_curated_outputs(tmp_path: Path) -> None:
    cfg = _build_config(tmp_path)

    run_pipeline(cfg)
    first_recommendations = pd.read_csv(cfg.processed_dir / "recommendations.csv")
    first_features = pd.read_csv(cfg.processed_dir / "customer_features.csv")

    run_pipeline(cfg)
    second_recommendations = pd.read_csv(cfg.processed_dir / "recommendations.csv")
    second_features = pd.read_csv(cfg.processed_dir / "customer_features.csv")

    pd.testing.assert_frame_equal(first_recommendations, second_recommendations)
    pd.testing.assert_frame_equal(first_features, second_features)


def test_failure_manifest_is_written(tmp_path: Path) -> None:
    cfg = _build_config(tmp_path, semantic_metrics_exists=False)

    with pytest.raises(PipelineStageError):
        run_pipeline(cfg)

    failure_manifests = list(cfg.manifests_dir.glob("*.failure.json"))
    assert len(failure_manifests) == 1
    payload = json.loads(failure_manifests[0].read_text(encoding="utf-8"))
    assert payload["status"] == "failed"
    assert payload["error_type"]
    assert payload["run_id"]


def test_kaggle_csv_parsing_creates_curated_raw_tables(tmp_path: Path) -> None:
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    source = raw_dir / "E-commerce Customer Behavior - Sheet1.csv"
    source.write_text(
        "\n".join(
            [
                "Customer ID,Gender,Age,City,Membership Type,Total Spend,Items Purchased,Average Rating,Discount Applied,Days Since Last Purchase,Satisfaction Level",
                "1,Male,31,Sao Paulo,Gold,900,3,4.8,Yes,14,High",
                "2,Female,28,Recife,Silver,450,2,4.3,No,35,Medium",
            ]
        ),
        encoding="utf-8",
    )

    cfg = _build_config(tmp_path)
    run_pipeline(cfg)

    customers = pd.read_csv(cfg.raw_dir / "customers.csv")
    orders = pd.read_csv(cfg.raw_dir / "orders.csv")
    assert {"customer_id", "channel", "segment", "signup_date"}.issubset(customers.columns)
    assert {"order_id", "customer_id", "order_value"}.issubset(orders.columns)


def test_data_dictionary_generation_from_contracts(tmp_path: Path) -> None:
    output_path = tmp_path / "dictionary.json"

    dictionary = build_data_dictionary(output_path)

    assert output_path.exists()
    assert dictionary["tables"]
    first_table = dictionary["tables"][0]
    assert {"table_name", "contract_model", "columns"} == set(first_table)


def test_retention_enforces_max_runs_and_age(tmp_path: Path) -> None:
    cfg = _build_config(tmp_path)
    cfg.ensure_directories()
    old_snapshot = cfg.snapshots_dir / "20240101T000000Z-old"
    mid_snapshot = cfg.snapshots_dir / "20240102T000000Z-mid"
    new_snapshot = cfg.snapshots_dir / "20240103T000000Z-new"
    for snapshot in [old_snapshot, mid_snapshot, new_snapshot]:
        snapshot.mkdir(parents=True, exist_ok=True)

    old_failure = cfg.manifests_dir / "old.failure.json"
    old_failure.write_text("{}", encoding="utf-8")

    old_ts = 1_700_000_000
    os.utime(old_snapshot, (old_ts, old_ts))
    os.utime(mid_snapshot, (old_ts + 100, old_ts + 100))
    os.utime(new_snapshot, (old_ts + 200, old_ts + 200))
    os.utime(old_failure, (old_ts, old_ts))

    retained_cfg = replace(
        cfg,
        snapshot_retention_days=1_000,
        snapshot_retention_runs=2,
        failure_retention_days=1,
    )

    _apply_retention(retained_cfg)

    remaining_snapshots = sorted(path.name for path in retained_cfg.snapshots_dir.iterdir())
    assert remaining_snapshots == ["20240102T000000Z-mid", "20240103T000000Z-new"]
    assert not old_failure.exists()


def test_cli_artifacts_command_generates_dictionary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_path = tmp_path / "dictionary.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["pipeline", "artifacts", "--data-dictionary-path", str(output_path)],
    )

    pipeline_main()

    assert output_path.exists()


def test_pipeline_config_reads_env_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "RIP_ENV=ci",
                "RIP_DATA_DIR=./custom-data",
                "RIP_SEED=123",
                "RIP_LOG_LEVEL=debug",
                "RIP_FRESHNESS_MAX_AGE_HOURS=12",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("RIP_ENV", raising=False)
    monkeypatch.delenv("RIP_DATA_DIR", raising=False)
    monkeypatch.delenv("RIP_SEED", raising=False)
    monkeypatch.delenv("RIP_LOG_LEVEL", raising=False)
    monkeypatch.delenv("RIP_FRESHNESS_MAX_AGE_HOURS", raising=False)

    cfg = PipelineConfig.from_env(tmp_path)

    assert cfg.env_name == "ci"
    assert cfg.data_dir == (tmp_path / "custom-data").resolve()
    assert cfg.seed == 123
    assert cfg.log_level == "DEBUG"
    assert cfg.freshness_max_age_hours == 12
