from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_sample_raw_data(raw_dir: Path = Path("data/raw")) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)

    customers = pd.DataFrame(
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
                "customer_city": "Rio de Janeiro",
                "customer_state": "RJ",
            },
            {
                "customer_id": "c3",
                "customer_unique_id": "u3",
                "customer_city": "Belo Horizonte",
                "customer_state": "MG",
            },
        ]
    )
    orders = pd.DataFrame(
        [
            {
                "order_id": "o1",
                "customer_id": "c1",
                "order_status": "delivered",
                "order_purchase_timestamp": "2018-01-10 10:00:00",
                "order_delivered_customer_date": "2018-01-14 12:00:00",
            },
            {
                "order_id": "o2",
                "customer_id": "c2",
                "order_status": "delivered",
                "order_purchase_timestamp": "2018-02-11 09:00:00",
                "order_delivered_customer_date": "2018-02-15 14:00:00",
            },
            {
                "order_id": "o3",
                "customer_id": "c2",
                "order_status": "delivered",
                "order_purchase_timestamp": "2018-03-20 17:00:00",
                "order_delivered_customer_date": "2018-03-24 10:00:00",
            },
            {
                "order_id": "o4",
                "customer_id": "c3",
                "order_status": "delivered",
                "order_purchase_timestamp": "2018-03-28 11:30:00",
                "order_delivered_customer_date": "2018-04-01 13:20:00",
            },
        ]
    )
    items = pd.DataFrame(
        [
            {
                "order_id": "o1",
                "order_item_id": 1,
                "price": 100.0,
                "freight_value": 12.0,
            },
            {
                "order_id": "o2",
                "order_item_id": 1,
                "price": 220.0,
                "freight_value": 15.0,
            },
            {
                "order_id": "o3",
                "order_item_id": 1,
                "price": 90.0,
                "freight_value": 10.0,
            },
            {
                "order_id": "o4",
                "order_item_id": 1,
                "price": 180.0,
                "freight_value": 13.0,
            },
        ]
    )
    payments = pd.DataFrame(
        [
            {"order_id": "o1", "payment_installments": 1, "payment_value": 112.0},
            {"order_id": "o2", "payment_installments": 2, "payment_value": 235.0},
            {"order_id": "o3", "payment_installments": 1, "payment_value": 100.0},
            {"order_id": "o4", "payment_installments": 3, "payment_value": 193.0},
        ]
    )

    customers.to_csv(raw_dir / "olist_customers_dataset.csv", index=False)
    orders.to_csv(raw_dir / "olist_orders_dataset.csv", index=False)
    items.to_csv(raw_dir / "olist_order_items_dataset.csv", index=False)
    payments.to_csv(raw_dir / "olist_order_payments_dataset.csv", index=False)


if __name__ == "__main__":
    write_sample_raw_data()
