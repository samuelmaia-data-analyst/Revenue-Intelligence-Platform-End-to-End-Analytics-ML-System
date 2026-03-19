from __future__ import annotations

import json
import logging
import re
import shutil
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

LOGGER = logging.getLogger("data_platform")
SNAPSHOT_INLINE_MAX_BYTES = 1_000_000


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
    artifact_snapshots: dict[str, list[str]] | None = None,
    snapshot_root: str | None = None,
    history_db_path: Path | None = None,
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
        "artifact_snapshots": artifact_snapshots or {},
        "snapshot_root": snapshot_root,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    write_run_catalog_entry(manifest_dir, manifest)
    if history_db_path is not None:
        write_run_history_record(history_db_path, manifest)
    return manifest_path


def snapshot_stage_artifacts(
    snapshot_dir: Path,
    *,
    stage: str,
    artifact_paths: list[str],
) -> list[str]:
    stage_snapshot_dir = snapshot_dir / stage
    ensure_dir(stage_snapshot_dir)
    snapshot_entries: list[str] = []

    for artifact in artifact_paths:
        source_path = Path(artifact)
        if not source_path.exists():
            LOGGER.warning("Skipping snapshot for missing artifact %s", source_path)
            continue

        metadata_path = source_path.with_suffix(".metadata.json")
        if metadata_path.exists():
            shutil.copy2(metadata_path, stage_snapshot_dir / metadata_path.name)

        artifact_size = source_path.stat().st_size
        if artifact_size <= SNAPSHOT_INLINE_MAX_BYTES:
            destination_path = stage_snapshot_dir / source_path.name
            shutil.copy2(source_path, destination_path)
            snapshot_entries.append(str(destination_path))
            continue

        pointer_path = stage_snapshot_dir / f"{source_path.stem}.snapshot.json"
        pointer_payload = {
            "artifact_name": source_path.name,
            "source_path": str(source_path),
            "metadata_path": (
                str(stage_snapshot_dir / metadata_path.name) if metadata_path.exists() else None
            ),
            "snapshot_mode": "metadata_only",
            "size_bytes": artifact_size,
            "inline_copy_threshold_bytes": SNAPSHOT_INLINE_MAX_BYTES,
        }
        pointer_path.write_text(json.dumps(pointer_payload, indent=2), encoding="utf-8")
        snapshot_entries.append(str(pointer_path))

    return snapshot_entries


def write_run_catalog_entry(manifest_dir: Path, manifest: Mapping[str, object]) -> Path:
    catalog_path = manifest_dir / "run_catalog.csv"
    catalog_columns = [
        "run_id",
        "command",
        "stage",
        "started_at_utc",
        "recorded_at_utc",
        "artifact_groups",
        "artifact_count",
        "snapshot_root",
    ]
    row = {
        "run_id": str(manifest.get("run_id", "")),
        "command": str(manifest.get("command", "")),
        "stage": str(manifest.get("stage", "")),
        "started_at_utc": str(manifest.get("started_at_utc", "")),
        "recorded_at_utc": str(manifest.get("recorded_at_utc", "")),
        "artifact_groups": 0,
        "artifact_count": 0,
        "snapshot_root": str(manifest.get("snapshot_root", "") or ""),
    }
    artifacts = manifest.get("artifacts", {})
    if isinstance(artifacts, dict):
        row["artifact_groups"] = len(artifacts)
        row["artifact_count"] = sum(
            len(paths) for paths in artifacts.values() if isinstance(paths, list)
        )

    if catalog_path.exists():
        catalog = pd.read_csv(catalog_path)
        catalog = catalog[catalog["run_id"] != row["run_id"]]
        updated_catalog = pd.concat([catalog, pd.DataFrame([row])], ignore_index=True)
    else:
        updated_catalog = pd.DataFrame([row], columns=catalog_columns)

    updated_catalog = updated_catalog.sort_values("started_at_utc", ascending=False)
    updated_catalog.to_csv(catalog_path, index=False)
    return catalog_path


def write_run_history_record(history_db_path: Path, manifest: Mapping[str, object]) -> Path:
    ensure_dir(history_db_path.parent)
    artifacts = manifest.get("artifacts", {})
    artifact_groups = 0
    artifact_count = 0
    if isinstance(artifacts, dict):
        artifact_groups = len(artifacts)
        artifact_count = sum(len(paths) for paths in artifacts.values() if isinstance(paths, list))

    with sqlite3.connect(history_db_path) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS run_history (
                run_id TEXT PRIMARY KEY,
                command TEXT NOT NULL,
                stage TEXT NOT NULL,
                started_at_utc TEXT NOT NULL,
                recorded_at_utc TEXT NOT NULL,
                artifact_groups INTEGER NOT NULL,
                artifact_count INTEGER NOT NULL,
                snapshot_root TEXT
            )
            """)
        connection.execute(
            """
            INSERT OR REPLACE INTO run_history (
                run_id,
                command,
                stage,
                started_at_utc,
                recorded_at_utc,
                artifact_groups,
                artifact_count,
                snapshot_root
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(manifest.get("run_id", "")),
                str(manifest.get("command", "")),
                str(manifest.get("stage", "")),
                str(manifest.get("started_at_utc", "")),
                str(manifest.get("recorded_at_utc", "")),
                artifact_groups,
                artifact_count,
                str(manifest.get("snapshot_root", "") or ""),
            ),
        )
        connection.commit()
    return history_db_path
