from __future__ import annotations

import json
import os
import shutil
import sqlite3
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def atomic_write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    _ensure_parent(path)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding=encoding,
        dir=path.parent,
        delete=False,
        suffix=".tmp",
    ) as tmp_file:
        tmp_file.write(content)
        temp_path = Path(tmp_file.name)
    os.replace(temp_path, path)


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def atomic_write_csv(path: Path, frame: pd.DataFrame) -> None:
    _ensure_parent(path)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        dir=path.parent,
        delete=False,
        suffix=".tmp",
    ) as tmp_file:
        frame.to_csv(tmp_file.name, index=False)
        temp_path = Path(tmp_file.name)
    os.replace(temp_path, path)


def atomic_copy_file(source: Path, destination: Path) -> None:
    _ensure_parent(destination)
    with tempfile.NamedTemporaryFile(
        dir=destination.parent, delete=False, suffix=".tmp"
    ) as tmp_file:
        temp_path = Path(tmp_file.name)
    shutil.copy2(source, temp_path)
    os.replace(temp_path, destination)


def atomic_copy_tree(source_dir: Path, destination_dir: Path) -> None:
    destination_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(
        tempfile.mkdtemp(prefix=f"{destination_dir.name}.", dir=str(destination_dir.parent))
    )
    try:
        for item in source_dir.iterdir():
            target = temp_dir / item.name
            if item.is_dir():
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)
        if destination_dir.exists():
            shutil.rmtree(destination_dir)
        os.replace(temp_dir, destination_dir)
    except Exception:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def replace_sqlite_database(database_path: Path, frames: dict[str, pd.DataFrame]) -> list[str]:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(dir=str(database_path.parent), suffix=".tmp")
    os.close(fd)
    temp_path = Path(temp_name)
    written_tables: list[str] = []
    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(temp_path)
        for table_name, frame in frames.items():
            frame.to_sql(table_name, connection, if_exists="replace", index=False)
            written_tables.append(table_name)
        connection.close()
        connection = None
        os.replace(temp_path, database_path)
    finally:
        if connection is not None:
            connection.close()
        if temp_path.exists():
            temp_path.unlink()
    return written_tables
