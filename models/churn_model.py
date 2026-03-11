from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split

from pipelines.common import read_csv_required


def train_churn_model(gold_dir: Path = Path("data/gold"), models_dir: Path = Path("models/artifacts")) -> dict[str, float]:
    models_dir.mkdir(parents=True, exist_ok=True)
    df = read_csv_required(
        gold_dir / "churn_features.csv",
        {"total_orders", "total_spent", "days_since_last_purchase", "avg_order_value", "is_churned"},
    )

    features = ["total_orders", "total_spent", "days_since_last_purchase", "avg_order_value"]
    x = df[features].fillna(0.0)
    y = df["is_churned"].astype(int)

    if y.nunique() < 2:
        metrics = {"accuracy": 1.0, "roc_auc": 1.0, "note": "single class target; model training skipped"}
        (models_dir / "churn_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        return metrics

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=42, stratify=y)
    model = LogisticRegression(max_iter=1000)
    model.fit(x_train, y_train)
    preds = model.predict(x_test)
    probs = model.predict_proba(x_test)[:, 1]

    metrics = {
        "accuracy": float(accuracy_score(y_test, preds)),
        "roc_auc": float(roc_auc_score(y_test, probs)),
    }
    (models_dir / "churn_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train churn model from gold features.")
    parser.add_argument("--gold-dir", type=Path, default=Path("data/gold"))
    parser.add_argument("--models-dir", type=Path, default=Path("models/artifacts"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    train_churn_model(args.gold_dir, args.models_dir)
