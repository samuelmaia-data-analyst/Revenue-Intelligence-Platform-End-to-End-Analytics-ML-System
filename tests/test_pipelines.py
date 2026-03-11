from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from models.revenue_forecasting import forecast_revenue
from pipelines.common import DataContractError
from pipelines.feature_pipeline import run_feature_engineering
from pipelines.ingestion_pipeline import run_ingestion
from pipelines.transformation_pipeline import run_transformation
from ridp.cli import build_parser


def _write_csv(path: Path, rows: list[dict]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


def _build_minimal_raw_dataset(raw_dir: Path) -> None:
    _write_csv(
        raw_dir / "olist_customers_dataset.csv",
        [
            {"customer_id": "c1", "customer_unique_id": "u1", "customer_city": "Sao Paulo", "customer_state": "SP"},
            {"customer_id": "c2", "customer_unique_id": "u2", "customer_city": "Rio", "customer_state": "RJ"},
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
    raw_dir.mkdir()
    _build_minimal_raw_dataset(raw_dir)

    ingested = run_ingestion(raw_dir, bronze_dir)
    assert len(ingested) == 4

    silver_outputs = run_transformation(bronze_dir, silver_dir)
    assert (silver_outputs["fct_orders"]).exists()
    assert (silver_outputs["dim_customers"]).exists()

    gold_outputs = run_feature_engineering(silver_dir, gold_dir)
    assert (gold_outputs["business_kpis"]).exists()
    kpi_df = pd.read_csv(gold_outputs["business_kpis"])
    assert "gmv_total" in set(kpi_df["metric"])


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


def test_forecast_requires_positive_horizon(tmp_path: Path) -> None:
    gold_dir = tmp_path / "gold"
    models_dir = tmp_path / "models"
    gold_dir.mkdir()
    _write_csv(gold_dir / "kpi_monthly_revenue.csv", [{"order_month": "2018-01", "revenue": 100.0}])

    with pytest.raises(ValueError, match="at least 1"):
        forecast_revenue(gold_dir, models_dir, periods=0)


def test_cli_parser_supports_full_pipeline_command() -> None:
    args = build_parser().parse_args(["run-pipeline", "all"])
    assert args.command == "run-pipeline"
    assert args.stage == "all"
