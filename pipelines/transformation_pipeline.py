from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from pipelines.common import LOGGER, configure_logging, ensure_dir, read_csv_required


def run_transformation(bronze_dir: Path, silver_dir: Path) -> dict[str, Path]:
    ensure_dir(silver_dir)

    customers = read_csv_required(
        bronze_dir / "olist_customers_dataset.csv",
        {"customer_id", "customer_unique_id", "customer_city", "customer_state"},
    )
    orders = read_csv_required(
        bronze_dir / "olist_orders_dataset.csv",
        {
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_delivered_customer_date",
        },
    )
    order_items = read_csv_required(
        bronze_dir / "olist_order_items_dataset.csv",
        {"order_id", "order_item_id", "price", "freight_value"},
    )
    order_payments = read_csv_required(
        bronze_dir / "olist_order_payments_dataset.csv",
        {"order_id", "payment_installments", "payment_value"},
    )

    customers = customers.drop_duplicates(subset=["customer_id"]).copy()
    customers = customers[["customer_id", "customer_unique_id", "customer_city", "customer_state"]]

    orders = orders.drop_duplicates(subset=["order_id"]).copy()
    for col in ["order_purchase_timestamp", "order_delivered_customer_date"]:
        if col in orders.columns:
            orders[col] = pd.to_datetime(orders[col], errors="coerce")

    order_items = order_items.copy()
    if "price" in order_items.columns:
        order_items["price"] = pd.to_numeric(order_items["price"], errors="coerce").fillna(0.0)
    if "freight_value" in order_items.columns:
        order_items["freight_value"] = pd.to_numeric(order_items["freight_value"], errors="coerce").fillna(0.0)

    payments = (
        order_payments.assign(
            payment_value=pd.to_numeric(order_payments["payment_value"], errors="coerce").fillna(0.0)
        )
        .groupby("order_id", as_index=False)
        .agg(
            total_payment_value=("payment_value", "sum"),
            payment_installments=("payment_installments", "max"),
        )
    )

    items_by_order = (
        order_items.groupby("order_id", as_index=False).agg(
            item_count=("order_item_id", "count"),
            gross_item_value=("price", "sum"),
            freight_value=("freight_value", "sum"),
        )
    )

    fct_orders = (
        orders.merge(payments, on="order_id", how="left")
        .merge(items_by_order, on="order_id", how="left")
        .fillna({"total_payment_value": 0.0, "payment_installments": 0, "item_count": 0, "gross_item_value": 0.0, "freight_value": 0.0})
    )

    customer_spend = (
        fct_orders.groupby("customer_id", as_index=False)
        .agg(
            total_orders=("order_id", "count"),
            total_spent=("total_payment_value", "sum"),
            first_purchase=("order_purchase_timestamp", "min"),
            last_purchase=("order_purchase_timestamp", "max"),
        )
    )
    dim_customers = customers.merge(customer_spend, on="customer_id", how="left")
    dim_customers[["total_orders", "total_spent"]] = dim_customers[["total_orders", "total_spent"]].fillna(0)

    output_paths = {
        "dim_customers": silver_dir / "dim_customers.csv",
        "fct_orders": silver_dir / "fct_orders.csv",
        "fct_order_items": silver_dir / "fct_order_items.csv",
    }
    dim_customers.to_csv(output_paths["dim_customers"], index=False)
    fct_orders.to_csv(output_paths["fct_orders"], index=False)
    order_items.to_csv(output_paths["fct_order_items"], index=False)

    LOGGER.info("Transformation complete. Wrote %d tables to %s", len(output_paths), silver_dir)
    return output_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run transformation pipeline (bronze -> silver).")
    parser.add_argument("--bronze-dir", type=Path, default=Path("data/bronze"))
    parser.add_argument("--silver-dir", type=Path, default=Path("data/silver"))
    return parser.parse_args()


if __name__ == "__main__":
    configure_logging()
    args = parse_args()
    run_transformation(args.bronze_dir, args.silver_dir)
