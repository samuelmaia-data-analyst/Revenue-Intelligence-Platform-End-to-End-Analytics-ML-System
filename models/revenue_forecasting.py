from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

from pipelines.common import LOGGER, read_csv_required


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def forecast_revenue(
    gold_dir: Path = Path("data/gold"),
    models_dir: Path = Path("models/artifacts"),
    periods: int = 3,
) -> pd.DataFrame:
    if periods < 1:
        raise ValueError("Forecast periods must be at least 1.")

    models_dir.mkdir(parents=True, exist_ok=True)
    monthly = read_csv_required(gold_dir / "kpi_monthly_revenue.csv", {"order_month", "revenue"})
    monthly = monthly.sort_values("order_month").reset_index(drop=True)

    if monthly.empty:
        out = pd.DataFrame(columns=["order_month", "predicted_revenue"])
        out.to_csv(models_dir / "revenue_forecast.csv", index=False)
        return out

    x = np.arange(len(monthly)).reshape(-1, 1)
    y = monthly["revenue"].to_numpy(dtype=float)

    model = LinearRegression()
    model.fit(x, y)
    in_sample_pred = model.predict(x)
    mae = float(mean_absolute_error(y, in_sample_pred))

    future_x = np.arange(len(monthly), len(monthly) + periods).reshape(-1, 1)
    future_pred = model.predict(future_x)

    last_period = pd.Period(monthly.iloc[-1]["order_month"], freq="M")
    future_months = [(last_period + i).strftime("%Y-%m") for i in range(1, periods + 1)]

    forecast = pd.DataFrame({"order_month": future_months, "predicted_revenue": future_pred})
    forecast.to_csv(models_dir / "revenue_forecast.csv", index=False)
    _write_json(
        models_dir / "revenue_forecast_metrics.json",
        {"mae_in_sample": mae, "periods": periods},
    )
    _write_json(
        models_dir / "revenue_forecast_model.json",
        {
            "model": "LinearRegression",
            "slope": float(model.coef_[0]),
            "intercept": float(model.intercept_),
            "training_points": int(len(monthly)),
        },
    )
    LOGGER.info(
        "Revenue forecast generated for %d future periods using %d historical points",
        periods,
        len(monthly),
    )
    return forecast


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train revenue forecasting model from monthly gold KPI."
    )
    parser.add_argument("--gold-dir", type=Path, default=Path("data/gold"))
    parser.add_argument("--models-dir", type=Path, default=Path("models/artifacts"))
    parser.add_argument("--periods", type=int, default=3)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    forecast_revenue(args.gold_dir, args.models_dir, periods=args.periods)
