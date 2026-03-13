from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


def persist_frames_to_sqlite(frames: dict[str, pd.DataFrame], database_path: Path) -> list[str]:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    written_tables: list[str] = []
    with sqlite3.connect(database_path) as connection:
        for table_name, frame in frames.items():
            frame.to_sql(table_name, connection, if_exists="replace", index=False)
            written_tables.append(table_name)
    return written_tables
