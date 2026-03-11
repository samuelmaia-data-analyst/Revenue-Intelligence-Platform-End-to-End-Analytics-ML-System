from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from pipelines.common import LOGGER, configure_logging, ensure_dir, read_csv_required


def run_feature_engineering(silver_dir: Path, gold_dir: Path) -> dict[str, Path]:
    ensure_dir(gold_dir)

    fct_orders = read_csv_required(
        silver_dir / "fct_orders.csv",
        {"order_id", "customer_id", "order_status", "order_purchase_timestamp", "total_payment_value"},
    )
    fct_orders["order_purchase_timestamp"] = pd.to_datetime(
        fct_orders["order_purchase_timestamp"], errors="coerce"
    )
    dim_customers = read_csv_required(
        silver_dir / "dim_customers.csv",
        {"customer_id", "total_orders", "total_spent", "first_purchase", "last_purchase"},
    )
    dim_customers["first_purchase"] = pd.to_datetime(dim_customers["first_purchase"], errors="coerce")
    dim_customers["last_purchase"] = pd.to_datetime(dim_customers["last_purchase"], errors="coerce")

    delivered_orders = fct_orders[fct_orders["order_status"] == "delivered"].copy()
    if delivered_orders.empty:
        raise ValueError("No delivered orders found in silver layer; gold KPIs cannot be computed.")
    delivered_orders["order_date"] = delivered_orders["order_purchase_timestamp"].dt.date
    delivered_orders["order_month"] = delivered_orders["order_purchase_timestamp"].dt.to_period("M").astype(str)

    daily_revenue = (
        delivered_orders.groupby("order_date", as_index=False)["total_payment_value"].sum().rename(
            columns={"total_payment_value": "revenue"}
        )
    )
    monthly_revenue = (
        delivered_orders.groupby("order_month", as_index=False)["total_payment_value"].sum().rename(
            columns={"total_payment_value": "revenue"}
        )
    )

    reference_date = delivered_orders["order_purchase_timestamp"].max()
    customer_360 = dim_customers.copy()
    customer_360["days_since_last_purchase"] = (
        reference_date - customer_360["last_purchase"]
    ).dt.days.fillna(9999).astype(int)
    customer_360["avg_order_value"] = (
        customer_360["total_spent"] / customer_360["total_orders"].replace({0: pd.NA})
    ).fillna(0.0)

    churn_features = customer_360[
        ["customer_id", "total_orders", "total_spent", "days_since_last_purchase", "avg_order_value"]
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
    daily_revenue.to_csv(output_paths["kpi_daily_revenue"], index=False)
    monthly_revenue.to_csv(output_paths["kpi_monthly_revenue"], index=False)
    customer_360.to_csv(output_paths["customer_360"], index=False)
    churn_features.to_csv(output_paths["churn_features"], index=False)
    business_kpis.to_csv(output_paths["business_kpis"], index=False)

    LOGGER.info("Feature engineering complete. Wrote %d gold tables to %s", len(output_paths), gold_dir)
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
