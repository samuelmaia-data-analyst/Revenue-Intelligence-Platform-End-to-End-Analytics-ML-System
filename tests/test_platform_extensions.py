import sqlite3
from pathlib import Path

import pandas as pd

from src.alerting import build_alert_report
from src.monitoring import build_monitoring_report
from src.persistence import persist_frames_to_sqlite
from src.reporting import simulate_action_portfolio
from src.semantic_metrics import build_metric_catalog
from src.writeback import append_approved_actions


def test_persist_frames_to_sqlite_creates_database_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "warehouse" / "test.db"
    frames = {
        "recommendations": pd.DataFrame({"customer_id": [1, 2], "ltv": [100.0, 200.0]}),
        "unit_economics": pd.DataFrame({"channel": ["Organic"], "ltv_cac_ratio": [4.2]}),
    }

    tables = persist_frames_to_sqlite(frames, db_path)

    assert db_path.exists()
    assert set(tables) == {"recommendations", "unit_economics"}

    with sqlite3.connect(db_path) as connection:
        persisted = pd.read_sql_query(
            "SELECT customer_id, ltv FROM recommendations ORDER BY customer_id",
            connection,
        )

    assert persisted["customer_id"].tolist() == [1, 2]


def test_build_monitoring_report_creates_drift_and_calibration_outputs(tmp_path: Path) -> None:
    scored = pd.DataFrame(
        {
            "recency_days": [10, 20, 35, 50, 80],
            "frequency": [5, 4, 3, 2, 1],
            "monetary": [1000.0, 800.0, 600.0, 300.0, 120.0],
            "avg_order_value": [200.0, 200.0, 200.0, 150.0, 120.0],
            "tenure_days": [300, 280, 200, 140, 90],
            "arpu": [100.0, 86.0, 90.0, 64.0, 40.0],
            "is_churned": [0, 0, 1, 1, 1],
            "next_purchase_30d": [1, 1, 0, 0, 0],
            "churn_probability": [0.1, 0.2, 0.7, 0.8, 0.9],
            "next_purchase_probability": [0.8, 0.75, 0.4, 0.2, 0.1],
        }
    )

    report = build_monitoring_report(
        scored_df=scored,
        labeled_df=scored,
        output_path=tmp_path / "monitoring_report.json",
        baseline_path=tmp_path / "monitoring_baseline.json",
    )

    assert report["drift_status"] == "initialized"
    assert report["calibration"]["churn"]["status"] == "ok"
    assert (tmp_path / "monitoring_report.json").exists()
    assert (tmp_path / "monitoring_baseline.json").exists()


def test_simulate_action_portfolio_respects_policy_overrides() -> None:
    recommendations = pd.DataFrame(
        {
            "customer_id": [1, 2],
            "channel": ["Organic", "Paid Search"],
            "segment": ["SMB", "Enterprise"],
            "ltv": [1000.0, 2000.0],
            "cac": [100.0, 300.0],
            "ltv_cac_ratio": [10.0, 6.67],
            "churn_probability": [0.8, 0.2],
            "next_purchase_probability": [0.3, 0.8],
            "strategic_score": [0.95, 0.85],
            "recommended_action": ["Retention Campaign", "Upsell Offer"],
        }
    )

    scenario = simulate_action_portfolio(
        recommendations_df=recommendations,
        top_n=2,
        policy_overrides={"Retention Campaign": {"uplift_rate": 0.5, "cost_rate": 0.1}},
    )

    assert "expected_uplift" in scenario.columns
    assert scenario.loc[scenario["customer_id"] == 1, "expected_uplift"].iloc[0] == 400.0


def test_build_metric_catalog_exports_semantic_definition(tmp_path: Path) -> None:
    definitions = tmp_path / "semantic_metrics.json"
    definitions.write_text(
        '{"version":"1.0","metrics":[{"name":"avg_ltv","expression":"avg(ltv)"}]}',
        encoding="utf-8",
    )

    catalog = build_metric_catalog(definitions, tmp_path / "catalog.json")

    assert catalog["version"] == "1.0"
    assert (tmp_path / "catalog.json").exists()


def test_build_alert_report_generates_warning_from_monitoring_and_quality(tmp_path: Path) -> None:
    monitoring = {
        "feature_drift": {"recency_days": {"status": "drift"}},
        "calibration": {"churn": {"status": "ok", "brier_score": 0.3}},
    }
    quality = {
        "datasets": [
            {
                "dataset_name": "silver_customers",
                "duplicate_rows": 1,
                "null_counts": {"channel": 0, "segment": 0},
            }
        ]
    }

    report = build_alert_report(monitoring, quality, tmp_path / "alerts_report.json")

    assert report["status"] == "warning"
    assert report["alert_count"] >= 1
    assert (tmp_path / "alerts_report.json").exists()


def test_append_approved_actions_writes_csv_and_warehouse(tmp_path: Path) -> None:
    approvals = pd.DataFrame(
        {
            "customer_id": [1],
            "recommended_action": ["Retention Campaign"],
            "approved_by": ["leader"],
            "approval_note": ["priority retention account"],
        }
    )

    result = append_approved_actions(
        approved_actions=approvals,
        csv_path=tmp_path / "approved_actions.csv",
        warehouse_target="sqlite",
        sqlite_path=tmp_path / "warehouse.db",
        warehouse_url=None,
    )

    assert "approval_timestamp_utc" in result.columns
    assert (tmp_path / "approved_actions.csv").exists()
    assert (tmp_path / "warehouse.db").exists()
