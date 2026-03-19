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
    models: Path
    runs: Path


@dataclass(frozen=True)
class RuntimeSettings:
    directories: DataDirectories
    log_level: str


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
        models=_path_from_env("RIDP_MODELS_DIR", "models/artifacts"),
        runs=_path_from_env("RIDP_RUNS_DIR", "data/run_manifests"),
    )


def get_runtime_settings() -> RuntimeSettings:
    return RuntimeSettings(
        directories=get_data_directories(),
        log_level=os.getenv("RIDP_LOG_LEVEL", "INFO").strip().upper(),
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
