from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

try:
    from sqlalchemy import create_engine
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    create_engine = None


def persist_frames_to_sqlite(frames: dict[str, pd.DataFrame], database_path: Path) -> list[str]:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    written_tables: list[str] = []
    with sqlite3.connect(database_path) as connection:
        for table_name, frame in frames.items():
            frame.to_sql(table_name, connection, if_exists="replace", index=False)
            written_tables.append(table_name)
    return written_tables


def persist_frames_to_postgres(frames: dict[str, pd.DataFrame], warehouse_url: str) -> list[str]:
    if create_engine is None:
        raise RuntimeError(
            "SQLAlchemy is required for Postgres persistence. Install SQLAlchemy and a Postgres driver."
        )
    engine = create_engine(warehouse_url)
    written_tables: list[str] = []
    with engine.begin() as connection:
        for table_name, frame in frames.items():
            frame.to_sql(table_name, connection, if_exists="replace", index=False)
            written_tables.append(table_name)
    return written_tables


def persist_frames(
    frames: dict[str, pd.DataFrame],
    warehouse_target: str,
    sqlite_path: Path,
    warehouse_url: str | None = None,
) -> list[str]:
    if warehouse_target == "sqlite":
        return persist_frames_to_sqlite(frames, sqlite_path)
    if warehouse_target == "postgres":
        if not warehouse_url:
            raise RuntimeError("RIP_WAREHOUSE_URL is required when RIP_WAREHOUSE_TARGET=postgres.")
        return persist_frames_to_postgres(frames, warehouse_url)
    raise RuntimeError(f"Unsupported warehouse target: {warehouse_target}")


def append_frame_to_warehouse(
    frame: pd.DataFrame,
    table_name: str,
    warehouse_target: str,
    sqlite_path: Path,
    warehouse_url: str | None = None,
) -> None:
    if warehouse_target == "sqlite":
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(sqlite_path) as connection:
            frame.to_sql(table_name, connection, if_exists="append", index=False)
        return

    if warehouse_target == "postgres":
        if create_engine is None:
            raise RuntimeError(
                "SQLAlchemy is required for Postgres persistence. Install SQLAlchemy and a Postgres driver."
            )
        if not warehouse_url:
            raise RuntimeError("RIP_WAREHOUSE_URL is required when RIP_WAREHOUSE_TARGET=postgres.")
        engine = create_engine(warehouse_url)
        with engine.begin() as connection:
            frame.to_sql(table_name, connection, if_exists="append", index=False)
        return

    raise RuntimeError(f"Unsupported warehouse target: {warehouse_target}")
