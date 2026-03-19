from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

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


def _load_customers(bronze_dir: Path) -> pd.DataFrame:
    customers = read_csv_required(
        bronze_dir / "olist_customers_dataset.csv",
        {"customer_id", "customer_unique_id", "customer_city", "customer_state"},
    )
    validate_non_empty(customers, "olist_customers_dataset.csv")
    validate_non_null_columns(
        customers,
        "olist_customers_dataset.csv",
        {"customer_id", "customer_unique_id", "customer_state"},
    )
    return (
        customers.drop_duplicates(subset=["customer_id"])
        .loc[:, ["customer_id", "customer_unique_id", "customer_city", "customer_state"]]
        .copy()
    )


def _load_orders(bronze_dir: Path) -> pd.DataFrame:
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
    validate_non_empty(orders, "olist_orders_dataset.csv")
    validate_non_null_columns(
        orders,
        "olist_orders_dataset.csv",
        {"order_id", "customer_id", "order_status", "order_purchase_timestamp"},
    )
    orders = orders.drop_duplicates(subset=["order_id"]).copy()

    for column in ["order_purchase_timestamp", "order_delivered_customer_date"]:
        orders[column] = pd.to_datetime(orders[column], errors="coerce")

    if orders["order_purchase_timestamp"].isna().any():
        raise DataContractError(
            "Table olist_orders_dataset.csv contains invalid order_purchase_timestamp values."
        )
    return orders


def _build_payments(bronze_dir: Path) -> pd.DataFrame:
    order_payments = read_csv_required(
        bronze_dir / "olist_order_payments_dataset.csv",
        {"order_id", "payment_installments", "payment_value"},
    )
    validate_non_empty(order_payments, "olist_order_payments_dataset.csv")
    validate_non_null_columns(
        order_payments,
        "olist_order_payments_dataset.csv",
        {"order_id", "payment_value"},
    )
    return (
        order_payments.assign(
            payment_value=pd.to_numeric(
                order_payments["payment_value"],
                errors="coerce",
            ).fillna(0.0)
        )
        .groupby("order_id", as_index=False)
        .agg(
            total_payment_value=("payment_value", "sum"),
            payment_installments=("payment_installments", "max"),
        )
    )


def _build_order_items(bronze_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    order_items = read_csv_required(
        bronze_dir / "olist_order_items_dataset.csv",
        {"order_id", "order_item_id", "price", "freight_value"},
    )
    validate_non_empty(order_items, "olist_order_items_dataset.csv")
    validate_non_null_columns(
        order_items,
        "olist_order_items_dataset.csv",
        {"order_id", "order_item_id"},
    )
    order_items = order_items.copy()
    order_items["price"] = pd.to_numeric(order_items["price"], errors="coerce").fillna(0.0)
    order_items["freight_value"] = pd.to_numeric(
        order_items["freight_value"],
        errors="coerce",
    ).fillna(0.0)

    items_by_order = order_items.groupby("order_id", as_index=False).agg(
        item_count=("order_item_id", "count"),
        gross_item_value=("price", "sum"),
        freight_value=("freight_value", "sum"),
    )
    return order_items, items_by_order


def run_transformation(
    bronze_dir: Path,
    silver_dir: Path,
    *,
    run_context: RunContext | None = None,
) -> dict[str, Path]:
    ensure_dir(silver_dir)
    customers = _load_customers(bronze_dir)
    orders = _load_orders(bronze_dir)
    payments = _build_payments(bronze_dir)
    order_items, items_by_order = _build_order_items(bronze_dir)

    fct_orders = (
        orders.merge(payments, on="order_id", how="left")
        .merge(items_by_order, on="order_id", how="left")
        .fillna(
            {
                "total_payment_value": 0.0,
                "payment_installments": 0,
                "item_count": 0,
                "gross_item_value": 0.0,
                "freight_value": 0.0,
            }
        )
    )
    validate_non_null_columns(
        fct_orders,
        "fct_orders.csv",
        {"order_id", "customer_id", "order_status", "order_purchase_timestamp"},
    )

    customer_spend = fct_orders.groupby("customer_id", as_index=False).agg(
        total_orders=("order_id", "count"),
        total_spent=("total_payment_value", "sum"),
        first_purchase=("order_purchase_timestamp", "min"),
        last_purchase=("order_purchase_timestamp", "max"),
    )
    dim_customers = customers.merge(customer_spend, on="customer_id", how="left")
    dim_customers[["total_orders", "total_spent"]] = dim_customers[
        ["total_orders", "total_spent"]
    ].fillna(0)

    output_paths = {
        "dim_customers": silver_dir / "dim_customers.csv",
        "fct_orders": silver_dir / "fct_orders.csv",
        "fct_order_items": silver_dir / "fct_order_items.csv",
    }
    write_dataframe(
        dim_customers,
        output_paths["dim_customers"],
        stage="transformation",
        source_tables=["olist_customers_dataset.csv", "olist_orders_dataset.csv"],
        run_context=run_context,
    )
    write_dataframe(
        fct_orders,
        output_paths["fct_orders"],
        stage="transformation",
        source_tables=[
            "olist_orders_dataset.csv",
            "olist_order_items_dataset.csv",
            "olist_order_payments_dataset.csv",
        ],
        run_context=run_context,
    )
    write_dataframe(
        order_items,
        output_paths["fct_order_items"],
        stage="transformation",
        source_tables=["olist_order_items_dataset.csv"],
        run_context=run_context,
    )

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
