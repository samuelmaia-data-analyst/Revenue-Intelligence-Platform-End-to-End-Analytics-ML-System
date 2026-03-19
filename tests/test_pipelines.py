from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from analytics.health_checks import evaluate_platform_health
from models.churn_model import train_churn_model
from models.revenue_forecasting import forecast_revenue
from pipelines.common import (
    SNAPSHOT_INLINE_MAX_BYTES,
    DataContractError,
    snapshot_stage_artifacts,
)
from pipelines.feature_pipeline import run_feature_engineering
from pipelines.ingestion_pipeline import run_ingestion
from pipelines.transformation_pipeline import run_transformation
from ridp.cli import build_parser, main


def _write_csv(path: Path, rows: list[dict]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


def _build_minimal_raw_dataset(raw_dir: Path) -> None:
    _write_csv(
        raw_dir / "olist_customers_dataset.csv",
        [
            {
                "customer_id": "c1",
                "customer_unique_id": "u1",
                "customer_city": "Sao Paulo",
                "customer_state": "SP",
            },
            {
                "customer_id": "c2",
                "customer_unique_id": "u2",
                "customer_city": "Rio",
                "customer_state": "RJ",
            },
        ],
    )
    _write_csv(
        raw_dir / "olist_orders_dataset.csv",
        [
            {
                "order_id": "o1",
                "customer_id": "c1",
                "order_status": "delivered",
                "order_purchase_timestamp": "2018-01-10 10:00:00",
                "order_delivered_customer_date": "2018-01-15 10:00:00",
            },
            {
                "order_id": "o2",
                "customer_id": "c2",
                "order_status": "delivered",
                "order_purchase_timestamp": "2018-03-10 10:00:00",
                "order_delivered_customer_date": "2018-03-12 10:00:00",
            },
        ],
    )
    _write_csv(
        raw_dir / "olist_order_items_dataset.csv",
        [
            {"order_id": "o1", "order_item_id": 1, "price": 100.0, "freight_value": 10.0},
            {"order_id": "o2", "order_item_id": 1, "price": 150.0, "freight_value": 12.0},
        ],
    )
    _write_csv(
        raw_dir / "olist_order_payments_dataset.csv",
        [
            {"order_id": "o1", "payment_installments": 1, "payment_value": 110.0},
            {"order_id": "o2", "payment_installments": 2, "payment_value": 162.0},
        ],
    )


def test_end_to_end_pipelines(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    bronze_dir = tmp_path / "bronze"
    silver_dir = tmp_path / "silver"
    gold_dir = tmp_path / "gold"
    serving_db = tmp_path / "serving.db"
    raw_dir.mkdir()
    _build_minimal_raw_dataset(raw_dir)

    ingested = run_ingestion(raw_dir, bronze_dir)
    assert len(ingested) == 4

    silver_outputs = run_transformation(bronze_dir, silver_dir)
    assert (silver_outputs["fct_orders"]).exists()
    assert (silver_outputs["dim_customers"]).exists()

    gold_outputs = run_feature_engineering(silver_dir, gold_dir, serving_db_path=serving_db)
    assert (gold_outputs["business_kpis"]).exists()
    kpi_df = pd.read_csv(gold_outputs["business_kpis"])
    assert "gmv_total" in set(kpi_df["metric"])
    metadata = json.loads((gold_dir / "business_kpis.metadata.json").read_text(encoding="utf-8"))
    assert metadata["stage"] == "feature_engineering"
    assert metadata["row_count"] == len(kpi_df)
    assert metadata["run_id"] is None
    with sqlite3.connect(serving_db) as connection:
        serving_tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name",
            connection,
        )
    assert "business_kpis" in set(serving_tables["name"])


def test_transformation_fails_with_clear_contract_error(tmp_path: Path) -> None:
    bronze_dir = tmp_path / "bronze"
    silver_dir = tmp_path / "silver"
    bronze_dir.mkdir()

    _write_csv(
        bronze_dir / "olist_customers_dataset.csv",
        [{"customer_id": "c1", "customer_unique_id": "u1", "customer_city": "Sao Paulo"}],
    )
    _write_csv(
        bronze_dir / "olist_orders_dataset.csv",
        [
            {
                "order_id": "o1",
                "customer_id": "c1",
                "order_status": "delivered",
                "order_purchase_timestamp": "2018-01-10 10:00:00",
                "order_delivered_customer_date": "2018-01-15 10:00:00",
            }
        ],
    )
    _write_csv(
        bronze_dir / "olist_order_items_dataset.csv",
        [{"order_id": "o1", "order_item_id": 1, "price": 100.0, "freight_value": 10.0}],
    )
    _write_csv(
        bronze_dir / "olist_order_payments_dataset.csv",
        [{"order_id": "o1", "payment_installments": 1, "payment_value": 110.0}],
    )

    with pytest.raises(DataContractError, match="customer_state"):
        run_transformation(bronze_dir, silver_dir)


def test_feature_engineering_rejects_missing_delivered_orders(tmp_path: Path) -> None:
    silver_dir = tmp_path / "silver"
    gold_dir = tmp_path / "gold"
    silver_dir.mkdir()

    _write_csv(
        silver_dir / "fct_orders.csv",
        [
            {
                "order_id": "o1",
                "customer_id": "c1",
                "order_status": "canceled",
                "order_purchase_timestamp": "2018-01-10 10:00:00",
                "total_payment_value": 110.0,
            }
        ],
    )
    _write_csv(
        silver_dir / "dim_customers.csv",
        [
            {
                "customer_id": "c1",
                "total_orders": 1,
                "total_spent": 110.0,
                "first_purchase": "2018-01-10 10:00:00",
                "last_purchase": "2018-01-10 10:00:00",
            }
        ],
    )

    with pytest.raises(ValueError, match="No delivered orders"):
        run_feature_engineering(silver_dir, gold_dir)


def test_transformation_rejects_invalid_purchase_timestamps(tmp_path: Path) -> None:
    bronze_dir = tmp_path / "bronze"
    silver_dir = tmp_path / "silver"
    bronze_dir.mkdir()

    _write_csv(
        bronze_dir / "olist_customers_dataset.csv",
        [
            {
                "customer_id": "c1",
                "customer_unique_id": "u1",
                "customer_city": "Sao Paulo",
                "customer_state": "SP",
            }
        ],
    )
    _write_csv(
        bronze_dir / "olist_orders_dataset.csv",
        [
            {
                "order_id": "o1",
                "customer_id": "c1",
                "order_status": "delivered",
                "order_purchase_timestamp": "not-a-date",
                "order_delivered_customer_date": "2018-01-15 10:00:00",
            }
        ],
    )
    _write_csv(
        bronze_dir / "olist_order_items_dataset.csv",
        [{"order_id": "o1", "order_item_id": 1, "price": 100.0, "freight_value": 10.0}],
    )
    _write_csv(
        bronze_dir / "olist_order_payments_dataset.csv",
        [{"order_id": "o1", "payment_installments": 1, "payment_value": 110.0}],
    )

    with pytest.raises(DataContractError, match="invalid order_purchase_timestamp"):
        run_transformation(bronze_dir, silver_dir)


def test_forecast_requires_positive_horizon(tmp_path: Path) -> None:
    gold_dir = tmp_path / "gold"
    models_dir = tmp_path / "models"
    gold_dir.mkdir()
    _write_csv(
        gold_dir / "kpi_monthly_revenue.csv",
        [{"order_month": "2018-01", "revenue": 100.0}],
    )

    with pytest.raises(ValueError, match="at least 1"):
        forecast_revenue(gold_dir, models_dir, periods=0)


def test_models_emit_explainability_artifacts(tmp_path: Path) -> None:
    gold_dir = tmp_path / "gold"
    models_dir = tmp_path / "models"
    gold_dir.mkdir()
    _write_csv(
        gold_dir / "churn_features.csv",
        [
            {
                "customer_id": "c1",
                "total_orders": 1,
                "total_spent": 100.0,
                "days_since_last_purchase": 10,
                "avg_order_value": 100.0,
                "is_churned": 0,
            },
            {
                "customer_id": "c2",
                "total_orders": 2,
                "total_spent": 160.0,
                "days_since_last_purchase": 120,
                "avg_order_value": 80.0,
                "is_churned": 1,
            },
            {
                "customer_id": "c3",
                "total_orders": 3,
                "total_spent": 300.0,
                "days_since_last_purchase": 20,
                "avg_order_value": 100.0,
                "is_churned": 0,
            },
            {
                "customer_id": "c4",
                "total_orders": 1,
                "total_spent": 90.0,
                "days_since_last_purchase": 150,
                "avg_order_value": 90.0,
                "is_churned": 1,
            },
        ],
    )
    _write_csv(
        gold_dir / "kpi_monthly_revenue.csv",
        [
            {"order_month": "2018-01", "revenue": 100.0},
            {"order_month": "2018-02", "revenue": 120.0},
            {"order_month": "2018-03", "revenue": 140.0},
        ],
    )

    churn_metrics = train_churn_model(gold_dir, models_dir)
    forecast = forecast_revenue(gold_dir, models_dir, periods=2)

    assert "accuracy" in churn_metrics
    assert len(forecast) == 2
    assert (models_dir / "churn_model_coefficients.json").exists()
    assert (models_dir / "revenue_forecast_model.json").exists()


def test_cli_parser_supports_full_pipeline_command() -> None:
    args = build_parser().parse_args(["run-pipeline", "all"])
    assert args.command == "run-pipeline"
    assert args.stage == "all"


def test_cli_pipeline_run_writes_manifest_and_run_id(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_dir = tmp_path / "raw"
    bronze_dir = tmp_path / "bronze"
    silver_dir = tmp_path / "silver"
    gold_dir = tmp_path / "gold"
    models_dir = tmp_path / "models"
    runs_dir = tmp_path / "run_manifests"
    run_artifacts_dir = tmp_path / "run_artifacts"
    raw_dir.mkdir()
    _build_minimal_raw_dataset(raw_dir)

    monkeypatch.setenv("RIDP_RAW_DIR", str(raw_dir))
    monkeypatch.setenv("RIDP_BRONZE_DIR", str(bronze_dir))
    monkeypatch.setenv("RIDP_SILVER_DIR", str(silver_dir))
    monkeypatch.setenv("RIDP_GOLD_DIR", str(gold_dir))
    monkeypatch.setenv("RIDP_SERVING_DB", str(tmp_path / "serving.db"))
    monkeypatch.setenv("RIDP_MODELS_DIR", str(models_dir))
    monkeypatch.setenv("RIDP_RUNS_DIR", str(runs_dir))
    monkeypatch.setenv("RIDP_RUN_ARTIFACTS_DIR", str(run_artifacts_dir))
    monkeypatch.setenv("RIDP_RUN_HISTORY_DB", str(runs_dir / "run_history.db"))
    monkeypatch.setattr(
        "sys.argv",
        ["ridp", "run-pipeline", "all", "--run-id", "test-run-001"],
    )

    main()

    manifest = json.loads((runs_dir / "test-run-001.json").read_text(encoding="utf-8"))
    assert manifest["run_id"] == "test-run-001"
    assert manifest["stage"] == "all"
    assert sorted(manifest["artifacts"]) == [
        "feature_engineering",
        "ingestion",
        "transformation",
    ]
    assert Path(manifest["snapshot_root"]).exists()
    assert (
        run_artifacts_dir / "test-run-001" / "feature_engineering" / "business_kpis.csv"
    ).exists()
    assert (
        run_artifacts_dir / "test-run-001" / "feature_engineering" / "business_kpis.metadata.json"
    ).exists()

    business_kpis_metadata = json.loads(
        (gold_dir / "business_kpis.metadata.json").read_text(encoding="utf-8")
    )
    assert business_kpis_metadata["run_id"] == "test-run-001"
    run_catalog = pd.read_csv(runs_dir / "run_catalog.csv")
    assert run_catalog.iloc[0]["run_id"] == "test-run-001"
    assert int(run_catalog.iloc[0]["artifact_count"]) >= 1
    with sqlite3.connect(runs_dir / "run_history.db") as connection:
        sql_history = pd.read_sql_query("SELECT * FROM run_history", connection)
    assert sql_history.iloc[0]["run_id"] == "test-run-001"


def test_snapshot_stage_artifacts_uses_pointer_files_for_large_outputs(tmp_path: Path) -> None:
    snapshot_root = tmp_path / "run_artifacts"
    artifact_path = tmp_path / "customer_360.csv"
    large_value = "x" * SNAPSHOT_INLINE_MAX_BYTES
    artifact_path.write_text(f"customer_id,notes\nc1,{large_value}\n", encoding="utf-8")
    metadata_path = artifact_path.with_suffix(".metadata.json")
    metadata_path.write_text(
        json.dumps(
            {
                "dataset_name": artifact_path.name,
                "row_count": 1,
                "generated_at_utc": "2026-03-19T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    snapshot_entries = snapshot_stage_artifacts(
        snapshot_root,
        stage="feature_engineering",
        artifact_paths=[str(artifact_path)],
    )

    stage_snapshot_dir = snapshot_root / "feature_engineering"
    pointer_path = stage_snapshot_dir / "customer_360.snapshot.json"
    assert snapshot_entries == [str(pointer_path)]
    assert not (stage_snapshot_dir / "customer_360.csv").exists()
    assert (stage_snapshot_dir / "customer_360.metadata.json").exists()
    pointer_payload = json.loads(pointer_path.read_text(encoding="utf-8"))
    assert pointer_payload["snapshot_mode"] == "metadata_only"
    assert pointer_payload["artifact_name"] == "customer_360.csv"
    assert int(pointer_payload["size_bytes"]) > SNAPSHOT_INLINE_MAX_BYTES


def test_health_check_reports_failures_and_warnings(tmp_path: Path) -> None:
    gold_dir = tmp_path / "gold"
    runs_dir = tmp_path / "runs"
    gold_dir.mkdir()
    runs_dir.mkdir()

    _write_csv(
        gold_dir / "business_kpis.csv",
        [{"metric": "gmv_total", "value": 100.0}],
    )
    (gold_dir / "business_kpis.metadata.json").write_text(
        json.dumps(
            {
                "dataset_name": "business_kpis.csv",
                "row_count": 1,
                "generated_at_utc": "2020-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    from ridp.config import DataDirectories

    monkey_dirs = DataDirectories(
        raw=tmp_path / "raw",
        bronze=tmp_path / "bronze",
        silver=tmp_path / "silver",
        gold=gold_dir,
        serving=tmp_path / "serving.db",
        models=tmp_path / "models",
        runs=runs_dir,
        run_artifacts=tmp_path / "run_artifacts",
        run_history_db=runs_dir / "run_history.db",
    )
    report = evaluate_platform_health(monkey_dirs, freshness_sla_hours=24)

    assert not report.failed.empty
    assert not report.warnings.empty
    assert "required_artifact_present" in set(report.checks["check_name"])


def test_cli_check_health_exits_non_zero_in_strict_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gold_dir = tmp_path / "gold"
    gold_dir.mkdir()
    _write_csv(
        gold_dir / "business_kpis.csv",
        [{"metric": "gmv_total", "value": 100.0}],
    )
    (gold_dir / "business_kpis.metadata.json").write_text(
        json.dumps(
            {
                "dataset_name": "business_kpis.csv",
                "row_count": 1,
                "generated_at_utc": "2020-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("RIDP_GOLD_DIR", str(gold_dir))
    monkeypatch.setenv("RIDP_RUNS_DIR", str(tmp_path / "runs"))
    monkeypatch.setenv("RIDP_RUN_HISTORY_DB", str(tmp_path / "runs" / "run_history.db"))
    monkeypatch.setenv("RIDP_SERVING_DB", str(tmp_path / "serving.db"))
    monkeypatch.setattr("sys.argv", ["ridp", "check-health", "--strict"])

    with pytest.raises(SystemExit, match="1"):
        main()
