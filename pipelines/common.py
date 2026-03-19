from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

LOGGER = logging.getLogger("data_platform")


class DataContractError(ValueError):
    """Raised when an input dataset does not match the expected contract."""


@dataclass(frozen=True)
class RunContext:
    run_id: str
    started_at_utc: str


def configure_logging(level: str | int = logging.INFO) -> None:
    resolved_level = logging.getLevelName(level.upper()) if isinstance(level, str) else level
    logging.basicConfig(
        level=resolved_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        force=True,
    )


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def build_run_context(run_id: str | None = None) -> RunContext:
    started_at = datetime.now(UTC).isoformat()
    resolved_run_id = run_id or datetime.now(UTC).strftime("run_%Y%m%dT%H%M%SZ")
    return RunContext(run_id=resolved_run_id, started_at_utc=started_at)


def normalize_columns(columns: list[str]) -> list[str]:
    normalized = []
    for col in columns:
        col = col.strip().lower()
        col = re.sub(r"[^a-z0-9]+", "_", col)
        col = col.strip("_")
        normalized.append(col)
    return normalized


def read_csv_required(path: Path, required_columns: set[str] | None = None) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required table: {path}")

    df = pd.read_csv(path)
    if required_columns:
        validate_required_columns(df, path.name, required_columns)
    return df


def validate_required_columns(
    df: pd.DataFrame,
    dataset_name: str,
    required_columns: set[str],
) -> None:
    missing = sorted(required_columns.difference(df.columns))
    if missing:
        missing_columns = ", ".join(missing)
        raise DataContractError(
            f"Table {dataset_name} is missing required columns: {missing_columns}"
        )


def validate_non_empty(df: pd.DataFrame, dataset_name: str) -> None:
    if df.empty:
        raise DataContractError(f"Table {dataset_name} is empty.")


def validate_non_null_columns(
    df: pd.DataFrame,
    dataset_name: str,
    required_non_null: set[str],
) -> None:
    null_columns = [column for column in sorted(required_non_null) if df[column].isna().any()]
    if null_columns:
        columns = ", ".join(null_columns)
        raise DataContractError(
            f"Table {dataset_name} has null values in required columns: {columns}"
        )


def write_dataframe(
    df: pd.DataFrame,
    output_path: Path,
    *,
    stage: str,
    source_tables: list[str],
    run_context: RunContext | None = None,
) -> Path:
    ensure_dir(output_path.parent)
    df.to_csv(output_path, index=False)

    metadata = {
        "dataset_name": output_path.name,
        "stage": stage,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "columns": list(df.columns),
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source_tables": source_tables,
        "run_id": run_context.run_id if run_context else None,
    }
    output_path.with_suffix(".metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )
    return output_path


def write_run_manifest(
    manifest_dir: Path,
    *,
    command: str,
    stage: str,
    run_context: RunContext,
    artifacts: dict[str, list[str]],
) -> Path:
    ensure_dir(manifest_dir)
    manifest_path = manifest_dir / f"{run_context.run_id}.json"
    manifest = {
        "run_id": run_context.run_id,
        "command": command,
        "stage": stage,
        "started_at_utc": run_context.started_at_utc,
        "recorded_at_utc": datetime.now(UTC).isoformat(),
        "artifacts": artifacts,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path
