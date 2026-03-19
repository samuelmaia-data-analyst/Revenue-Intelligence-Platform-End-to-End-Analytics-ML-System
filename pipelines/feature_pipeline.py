from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from analytics.serving_store import materialize_gold_to_serving_store
from pipelines.common import (
    LOGGER,
    DataContractError,
    RunContext,
    configure_logging,
    ensure_dir,
    read_csv_required,
    validate_non_empty,
    validate_non_null_columns,
    write_dataframe,
)


def _load_orders(silver_dir: Path) -> pd.DataFrame:
    fct_orders = read_csv_required(
        silver_dir / "fct_orders.csv",
        {
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "total_payment_value",
        },
    )
    validate_non_empty(fct_orders, "fct_orders.csv")
    validate_non_null_columns(
        fct_orders,
        "fct_orders.csv",
        {"order_id", "customer_id", "order_status", "order_purchase_timestamp"},
    )
    fct_orders = fct_orders.copy()
    fct_orders["order_purchase_timestamp"] = pd.to_datetime(
        fct_orders["order_purchase_timestamp"],
        errors="coerce",
    )
    if fct_orders["order_purchase_timestamp"].isna().any():
        raise DataContractError(
            "Table fct_orders.csv contains invalid order_purchase_timestamp values."
        )
    return fct_orders


def _load_customers(silver_dir: Path) -> pd.DataFrame:
    dim_customers = read_csv_required(
        silver_dir / "dim_customers.csv",
        {
            "customer_id",
            "total_orders",
            "total_spent",
            "first_purchase",
            "last_purchase",
        },
    )
    validate_non_empty(dim_customers, "dim_customers.csv")
    validate_non_null_columns(dim_customers, "dim_customers.csv", {"customer_id"})
    dim_customers = dim_customers.copy()
    dim_customers["first_purchase"] = pd.to_datetime(
        dim_customers["first_purchase"], errors="coerce"
    )
    dim_customers["last_purchase"] = pd.to_datetime(
        dim_customers["last_purchase"],
        errors="coerce",
    )
    return dim_customers


def _build_revenue_outputs(
    delivered_orders: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    daily_revenue = (
        delivered_orders.groupby("order_date", as_index=False)
        .agg(revenue=("total_payment_value", "sum"))
        .sort_values("order_date")
    )
    monthly_revenue = (
        delivered_orders.groupby("order_month", as_index=False)
        .agg(revenue=("total_payment_value", "sum"))
        .sort_values("order_month")
    )
    return daily_revenue, monthly_revenue


def _build_customer_360(
    dim_customers: pd.DataFrame,
    reference_date: pd.Timestamp,
) -> pd.DataFrame:
    customer_360 = dim_customers.copy()
    customer_360["days_since_last_purchase"] = (
        (reference_date - customer_360["last_purchase"]).dt.days.fillna(9999).astype(int)
    )
    customer_360["avg_order_value"] = np.where(
        customer_360["total_orders"].fillna(0) > 0,
        customer_360["total_spent"].fillna(0.0) / customer_360["total_orders"].fillna(0),
        0.0,
    )
    return customer_360


def run_feature_engineering(
    silver_dir: Path,
    gold_dir: Path,
    *,
    run_context: RunContext | None = None,
    serving_db_path: Path | None = None,
) -> dict[str, Path]:
    ensure_dir(gold_dir)

    fct_orders = _load_orders(silver_dir)
    dim_customers = _load_customers(silver_dir)

    delivered_orders = fct_orders[fct_orders["order_status"] == "delivered"].copy()
    if delivered_orders.empty:
        raise ValueError("No delivered orders found in silver layer; gold KPIs cannot be computed.")
    delivered_orders["order_date"] = delivered_orders["order_purchase_timestamp"].dt.date
    delivered_orders["order_month"] = (
        delivered_orders["order_purchase_timestamp"].dt.to_period("M").astype(str)
    )

    daily_revenue, monthly_revenue = _build_revenue_outputs(delivered_orders)

    reference_date = delivered_orders["order_purchase_timestamp"].max()
    customer_360 = _build_customer_360(dim_customers, reference_date)

    churn_features = customer_360[
        [
            "customer_id",
            "total_orders",
            "total_spent",
            "days_since_last_purchase",
            "avg_order_value",
        ]
    ].copy()
    churn_features["is_churned"] = (churn_features["days_since_last_purchase"] > 90).astype(int)

    business_kpis = pd.DataFrame(
        [
            {
                "metric": "gmv_total",
                "value": float(delivered_orders["total_payment_value"].sum()),
            },
            {
                "metric": "aov",
                "value": float(
                    delivered_orders["total_payment_value"].sum()
                    / max(delivered_orders["order_id"].nunique(), 1)
                ),
            },
            {
                "metric": "active_customers",
                "value": float(delivered_orders["customer_id"].nunique()),
            },
            {
                "metric": "churn_rate_proxy",
                "value": float(churn_features["is_churned"].mean()),
            },
        ]
    )

    output_paths = {
        "kpi_daily_revenue": gold_dir / "kpi_daily_revenue.csv",
        "kpi_monthly_revenue": gold_dir / "kpi_monthly_revenue.csv",
        "customer_360": gold_dir / "customer_360.csv",
        "churn_features": gold_dir / "churn_features.csv",
        "business_kpis": gold_dir / "business_kpis.csv",
    }
    write_dataframe(
        daily_revenue,
        output_paths["kpi_daily_revenue"],
        stage="feature_engineering",
        source_tables=["fct_orders.csv"],
        run_context=run_context,
    )
    write_dataframe(
        monthly_revenue,
        output_paths["kpi_monthly_revenue"],
        stage="feature_engineering",
        source_tables=["fct_orders.csv"],
        run_context=run_context,
    )
    write_dataframe(
        customer_360,
        output_paths["customer_360"],
        stage="feature_engineering",
        source_tables=["dim_customers.csv", "fct_orders.csv"],
        run_context=run_context,
    )
    write_dataframe(
        churn_features,
        output_paths["churn_features"],
        stage="feature_engineering",
        source_tables=["customer_360.csv"],
        run_context=run_context,
    )
    write_dataframe(
        business_kpis,
        output_paths["business_kpis"],
        stage="feature_engineering",
        source_tables=["fct_orders.csv", "churn_features.csv"],
        run_context=run_context,
    )

    LOGGER.info(
        "Feature engineering complete. Wrote %d gold tables to %s",
        len(output_paths),
        gold_dir,
    )
    if serving_db_path is not None:
        materialize_gold_to_serving_store(
            gold_dir,
            serving_db_path,
            run_id=run_context.run_id if run_context else None,
        )
        LOGGER.info("Serving store refreshed at %s", serving_db_path)
    return output_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run feature pipeline (silver -> gold).")
    parser.add_argument("--silver-dir", type=Path, default=Path("data/silver"))
    parser.add_argument("--gold-dir", type=Path, default=Path("data/gold"))
    return parser.parse_args()


if __name__ == "__main__":
    configure_logging()
    args = parse_args()
    run_feature_engineering(args.silver_dir, args.gold_dir)
