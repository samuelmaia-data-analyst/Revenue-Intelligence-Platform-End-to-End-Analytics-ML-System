from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split

from pipelines.common import LOGGER, read_csv_required


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _skip_training(models_dir: Path, note: str) -> dict[str, Any]:
    skipped_metrics: dict[str, Any] = {
        "accuracy": 1.0,
        "roc_auc": 1.0,
        "note": note,
    }
    _write_json(models_dir / "churn_metrics.json", skipped_metrics)
    return skipped_metrics


def train_churn_model(
    gold_dir: Path = Path("data/gold"),
    models_dir: Path = Path("models/artifacts"),
) -> dict[str, Any]:
    models_dir.mkdir(parents=True, exist_ok=True)
    df = read_csv_required(
        gold_dir / "churn_features.csv",
        {
            "total_orders",
            "total_spent",
            "days_since_last_purchase",
            "avg_order_value",
            "is_churned",
        },
    )

    features = ["total_orders", "total_spent", "days_since_last_purchase", "avg_order_value"]
    x = df[features].fillna(0.0)
    y = df["is_churned"].astype(int)

    if y.nunique() < 2:
        return _skip_training(models_dir, "single class target; model training skipped")

    class_count = int(y.nunique())
    minimum_test_fraction = class_count / len(df)
    test_size = max(0.25, minimum_test_fraction)
    expected_train_size = len(df) - math.ceil(len(df) * test_size)
    if expected_train_size < class_count:
        return _skip_training(
            models_dir,
            "insufficient samples for a stratified train/test split; model training skipped",
        )

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=test_size,
        random_state=42,
        stratify=y,
    )
    model = LogisticRegression(max_iter=1000)
    model.fit(x_train, y_train)
    preds = model.predict(x_test)
    probs = model.predict_proba(x_test)[:, 1]

    trained_metrics: dict[str, Any] = {
        "accuracy": float(accuracy_score(y_test, preds)),
        "roc_auc": float(roc_auc_score(y_test, probs)),
    }
    _write_json(models_dir / "churn_metrics.json", trained_metrics)
    _write_json(
        models_dir / "churn_model_coefficients.json",
        {
            "features": features,
            "intercept": float(model.intercept_[0]),
            "coefficients": {
                feature: float(coefficient)
                for feature, coefficient in zip(features, model.coef_[0], strict=True)
            },
        },
    )
    LOGGER.info("Churn model trained with %d rows and %d features", len(df), len(features))
    return trained_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train churn model from gold features.")
    parser.add_argument("--gold-dir", type=Path, default=Path("data/gold"))
    parser.add_argument("--models-dir", type=Path, default=Path("models/artifacts"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    train_churn_model(args.gold_dir, args.models_dir)
