from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from pipelines.common import ensure_dir, read_csv_required

SERVING_TABLES: tuple[str, ...] = (
    "business_kpis",
    "kpi_daily_revenue",
    "kpi_monthly_revenue",
    "customer_360",
    "churn_features",
)


def materialize_gold_to_serving_store(
    gold_dir: Path,
    serving_db_path: Path,
    *,
    run_id: str | None,
) -> Path:
    ensure_dir(serving_db_path.parent)
    datasets = {
        "business_kpis": read_csv_required(gold_dir / "business_kpis.csv", {"metric", "value"}),
        "kpi_daily_revenue": read_csv_required(
            gold_dir / "kpi_daily_revenue.csv",
            {"order_date", "revenue"},
        ),
        "kpi_monthly_revenue": read_csv_required(
            gold_dir / "kpi_monthly_revenue.csv",
            {"order_month", "revenue"},
        ),
        "customer_360": read_csv_required(
            gold_dir / "customer_360.csv",
            {"customer_id", "total_orders", "total_spent"},
        ),
        "churn_features": read_csv_required(
            gold_dir / "churn_features.csv",
            {"customer_id", "is_churned"},
        ),
    }

    with sqlite3.connect(serving_db_path) as connection:
        for table_name, dataframe in datasets.items():
            dataframe.to_sql(table_name, connection, if_exists="replace", index=False)

        serving_runs = pd.DataFrame(
            [
                {
                    "run_id": run_id or "",
                    "materialized_at_utc": pd.Timestamp.utcnow().isoformat(),
                    "source_gold_dir": str(gold_dir),
                    "table_count": len(datasets),
                }
            ]
        )
        serving_runs.to_sql("serving_runs", connection, if_exists="append", index=False)

    return serving_db_path


def load_serving_table(serving_db_path: Path, table_name: str) -> pd.DataFrame:
    with sqlite3.connect(serving_db_path) as connection:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", connection)
