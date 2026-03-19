from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st

from analytics.business_metrics import cohort_retention
from analytics.kpi_metrics import kpi_dict
from pipelines.common import read_csv_required
from ridp.config import (
    DashboardSettings,
    DataDirectories,
    get_dashboard_settings,
    get_data_directories,
)


@dataclass(frozen=True)
class DashboardData:
    metrics: dict[str, float]
    monthly_revenue: pd.DataFrame
    customer_360: pd.DataFrame
    retention: pd.DataFrame


@dataclass(frozen=True)
class RunHistoryData:
    manifests: pd.DataFrame
    artifact_history: pd.DataFrame


@dataclass(frozen=True)
class DashboardSourcePaths:
    gold_dir: Path
    run_dir: Path
    demo_mode: str
    demo_active: bool


def _gold_layer_ready(gold_dir: Path) -> bool:
    required_files = (
        "business_kpis.csv",
        "kpi_monthly_revenue.csv",
        "customer_360.csv",
    )
    return all((gold_dir / file_name).exists() for file_name in required_files)


def resolve_dashboard_sources(
    directories: DataDirectories | None = None,
    settings: DashboardSettings | None = None,
) -> DashboardSourcePaths:
    resolved_directories = directories or get_data_directories()
    resolved_settings = settings or get_dashboard_settings()
    selected_mode = st.session_state.get("dashboard_source_mode")
    if isinstance(selected_mode, str) and selected_mode in {"AUTO", "ON", "OFF"}:
        resolved_settings = DashboardSettings(
            demo_mode=selected_mode,
            demo_assets_root=resolved_settings.demo_assets_root,
        )
    demo_gold_dir = resolved_settings.demo_assets_root / "gold"
    demo_run_dir = resolved_settings.demo_assets_root / "runs"

    if resolved_settings.demo_mode == "ON":
        return DashboardSourcePaths(
            gold_dir=demo_gold_dir,
            run_dir=demo_run_dir,
            demo_mode=resolved_settings.demo_mode,
            demo_active=True,
        )

    primary_ready = _gold_layer_ready(resolved_directories.gold)
    if primary_ready or resolved_settings.demo_mode == "OFF":
        return DashboardSourcePaths(
            gold_dir=resolved_directories.gold,
            run_dir=resolved_directories.runs,
            demo_mode=resolved_settings.demo_mode,
            demo_active=False,
        )

    return DashboardSourcePaths(
        gold_dir=demo_gold_dir,
        run_dir=demo_run_dir,
        demo_mode=resolved_settings.demo_mode,
        demo_active=True,
    )


@st.cache_data(show_spinner=False)
def load_dashboard_data(gold_dir: str) -> DashboardData:
    base_path = Path(gold_dir)
    metrics = kpi_dict(base_path)
    monthly_revenue = read_csv_required(
        base_path / "kpi_monthly_revenue.csv",
        {"order_month", "revenue"},
    ).sort_values("order_month")
    customer_360 = read_csv_required(
        base_path / "customer_360.csv",
        {
            "customer_id",
            "total_orders",
            "total_spent",
            "first_purchase",
            "last_purchase",
            "days_since_last_purchase",
            "avg_order_value",
        },
    )
    customer_360["first_purchase"] = pd.to_datetime(
        customer_360["first_purchase"],
        errors="coerce",
    )
    customer_360["last_purchase"] = pd.to_datetime(
        customer_360["last_purchase"],
        errors="coerce",
    )
    retention = cohort_retention(base_path)
    return DashboardData(
        metrics=metrics,
        monthly_revenue=monthly_revenue,
        customer_360=customer_360,
        retention=retention,
    )


@st.cache_data(show_spinner=False)
def load_run_history(run_dir: str) -> RunHistoryData:
    base_path = Path(run_dir)
    manifest_rows: list[dict[str, object]] = []
    artifact_rows: list[dict[str, object]] = []

    if not base_path.exists():
        empty_manifest = pd.DataFrame(
            columns=["run_id", "command", "stage", "started_at_utc", "recorded_at_utc"]
        )
        empty_artifacts = pd.DataFrame(columns=["run_id", "stage_name", "artifact_path"])
        return RunHistoryData(manifests=empty_manifest, artifact_history=empty_artifacts)

    for manifest_path in sorted(base_path.glob("*.json")):
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_rows.append(
            {
                "run_id": payload.get("run_id", manifest_path.stem),
                "command": payload.get("command", ""),
                "stage": payload.get("stage", ""),
                "started_at_utc": payload.get("started_at_utc", ""),
                "recorded_at_utc": payload.get("recorded_at_utc", ""),
                "artifact_groups": len(payload.get("artifacts", {})),
            }
        )
        artifacts = payload.get("artifacts", {})
        if isinstance(artifacts, dict):
            for stage_name, stage_artifacts in artifacts.items():
                if isinstance(stage_artifacts, list):
                    for artifact_path in stage_artifacts:
                        artifact_rows.append(
                            {
                                "run_id": payload.get("run_id", manifest_path.stem),
                                "stage_name": stage_name,
                                "artifact_path": str(artifact_path),
                            }
                        )

    manifests = pd.DataFrame(manifest_rows).sort_values(
        "started_at_utc",
        ascending=False,
    )
    artifact_history = pd.DataFrame(artifact_rows)
    return RunHistoryData(manifests=manifests, artifact_history=artifact_history)
