from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from urllib import request

from src.io_utils import atomic_write_json


def _default_thresholds() -> dict[str, float | int]:
    return {
        "drift_feature_count_warn": float(os.getenv("RIP_ALERT_DRIFT_FEATURE_COUNT_WARN", "1")),
        "duplicate_rows_warn": float(os.getenv("RIP_ALERT_DUPLICATE_ROWS_WARN", "0")),
        "null_count_warn": float(os.getenv("RIP_ALERT_NULL_COUNT_WARN", "0")),
        "brier_score_warn": float(os.getenv("RIP_ALERT_BRIER_SCORE_WARN", "0.25")),
    }


def build_alert_report(
    monitoring_report: dict,
    quality_report: dict,
    output_path: Path,
    thresholds: dict[str, float | int] | None = None,
) -> dict:
    active_thresholds = thresholds or _default_thresholds()
    alerts: list[dict[str, str | float | int]] = []

    drift_count = sum(
        1
        for item in monitoring_report.get("feature_drift", {}).values()
        if item.get("status") in {"watch", "drift"}
    )
    if drift_count >= float(active_thresholds["drift_feature_count_warn"]):
        alerts.append(
            {
                "category": "monitoring",
                "severity": "warning",
                "message": f"{drift_count} features are in watch/drift state.",
            }
        )

    for dataset in quality_report.get("datasets", []):
        if int(dataset.get("duplicate_rows", 0)) > float(active_thresholds["duplicate_rows_warn"]):
            alerts.append(
                {
                    "category": "quality",
                    "severity": "warning",
                    "message": (
                        f"{dataset['dataset_name']} has {dataset['duplicate_rows']} duplicate rows/keys."
                    ),
                }
            )
        null_total = sum(int(value) for value in dataset.get("null_counts", {}).values())
        if null_total > float(active_thresholds["null_count_warn"]):
            alerts.append(
                {
                    "category": "quality",
                    "severity": "warning",
                    "message": f"{dataset['dataset_name']} has {null_total} null values in total.",
                }
            )

    for model_name, calibration in monitoring_report.get("calibration", {}).items():
        brier = calibration.get("brier_score")
        if calibration.get("status") == "ok" and brier is not None:
            if float(brier) >= float(active_thresholds["brier_score_warn"]):
                alerts.append(
                    {
                        "category": "calibration",
                        "severity": "warning",
                        "message": f"{model_name} brier score is {float(brier):.3f}.",
                    }
                )

    report = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "thresholds": active_thresholds,
        "alert_count": len(alerts),
        "status": "warning" if alerts else "ok",
        "alerts": alerts,
    }
    atomic_write_json(output_path, report)
    return report


def dispatch_alerts(report: dict) -> None:
    webhook_url = os.getenv("RIP_ALERT_WEBHOOK_URL", "").strip()
    if not webhook_url or report.get("alert_count", 0) == 0:
        return

    payload = json.dumps(report).encode("utf-8")
    req = request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=10) as response:  # pragma: no cover - network dependent
        response.read()
