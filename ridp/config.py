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
    )
