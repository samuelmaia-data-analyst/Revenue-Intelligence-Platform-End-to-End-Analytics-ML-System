from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_kpis(gold_dir: Path = Path("data/gold")) -> pd.DataFrame:
    return pd.read_csv(gold_dir / "business_kpis.csv")


def kpi_dict(gold_dir: Path = Path("data/gold")) -> dict[str, float]:
    df = load_kpis(gold_dir)
    return {row["metric"]: float(row["value"]) for _, row in df.iterrows()}

