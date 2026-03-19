from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class DataDirectories:
    raw: Path
    bronze: Path
    silver: Path
    gold: Path
    serving: Path
    models: Path
    runs: Path
    run_artifacts: Path
    run_history_db: Path


@dataclass(frozen=True)
class RuntimeSettings:
    directories: DataDirectories
    log_level: str
    freshness_sla_hours: int


@dataclass(frozen=True)
class DashboardSettings:
    demo_mode: str
    demo_assets_root: Path


def _path_from_env(env_name: str, default: str) -> Path:
    value = os.getenv(env_name, default).strip()
    return (PROJECT_ROOT / value).resolve() if not Path(value).is_absolute() else Path(value)


def get_data_directories() -> DataDirectories:
    return DataDirectories(
        raw=_path_from_env("RIDP_RAW_DIR", "data/raw"),
        bronze=_path_from_env("RIDP_BRONZE_DIR", "data/bronze"),
        silver=_path_from_env("RIDP_SILVER_DIR", "data/silver"),
        gold=_path_from_env("RIDP_GOLD_DIR", "data/gold"),
        serving=_path_from_env("RIDP_SERVING_DB", "data/serving/revenue_serving.db"),
        models=_path_from_env("RIDP_MODELS_DIR", "models/artifacts"),
        runs=_path_from_env("RIDP_RUNS_DIR", "data/run_manifests"),
        run_artifacts=_path_from_env("RIDP_RUN_ARTIFACTS_DIR", "data/run_artifacts"),
        run_history_db=_path_from_env("RIDP_RUN_HISTORY_DB", "data/run_manifests/run_history.db"),
    )


def get_runtime_settings() -> RuntimeSettings:
    sla_value = os.getenv("RIDP_FRESHNESS_SLA_HOURS", "24").strip()
    freshness_sla_hours = int(sla_value) if sla_value.isdigit() and int(sla_value) > 0 else 24
    return RuntimeSettings(
        directories=get_data_directories(),
        log_level=os.getenv("RIDP_LOG_LEVEL", "INFO").strip().upper(),
        freshness_sla_hours=freshness_sla_hours,
    )


def get_dashboard_settings() -> DashboardSettings:
    demo_mode = os.getenv("RIDP_DASHBOARD_DEMO_MODE", "AUTO").strip().upper()
    if demo_mode not in {"AUTO", "ON", "OFF"}:
        demo_mode = "AUTO"
    return DashboardSettings(
        demo_mode=demo_mode,
        demo_assets_root=_path_from_env(
            "RIDP_DASHBOARD_DEMO_ASSETS_DIR",
            "dashboard/demo_assets",
        ),
    )
