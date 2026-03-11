from __future__ import annotations

from pathlib import Path
import logging
import re

import pandas as pd


LOGGER = logging.getLogger("data_platform")


class DataContractError(ValueError):
    """Raised when an input dataset does not match the expected contract."""


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


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
        missing = sorted(required_columns.difference(df.columns))
        if missing:
            raise DataContractError(f"Table {path.name} is missing required columns: {', '.join(missing)}")
    return df
