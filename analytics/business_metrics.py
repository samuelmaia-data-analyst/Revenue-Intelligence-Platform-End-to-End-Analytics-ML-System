from __future__ import annotations

from pathlib import Path

import pandas as pd

from pipelines.common import read_csv_required


def cohort_retention(gold_dir: Path = Path("data/gold")) -> pd.DataFrame:
    customer_360 = read_csv_required(
        gold_dir / "customer_360.csv",
        {"customer_id", "first_purchase", "last_purchase", "days_since_last_purchase"},
    )
    customer_360["first_purchase"] = pd.to_datetime(
        customer_360["first_purchase"],
        errors="coerce",
    )
    customer_360["last_purchase"] = pd.to_datetime(
        customer_360["last_purchase"],
        errors="coerce",
    )
    df = customer_360.dropna(subset=["first_purchase", "last_purchase"]).copy()
    if df.empty:
        return pd.DataFrame(
            columns=["cohort_month", "retained_customers", "customers", "retention_rate"]
        )

    df["cohort_month"] = df["first_purchase"].dt.to_period("M").astype(str)
    retained = (df["days_since_last_purchase"] <= 90).astype(int)

    out = (
        df.assign(retained=retained)
        .groupby("cohort_month", as_index=False)
        .agg(customers=("customer_id", "count"), retained_customers=("retained", "sum"))
    )
    out["retention_rate"] = out["retained_customers"] / out["customers"]
    return out.sort_values("cohort_month")
