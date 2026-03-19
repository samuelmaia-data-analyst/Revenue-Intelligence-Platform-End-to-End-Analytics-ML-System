from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from pipelines.common import (
    LOGGER,
    RunContext,
    configure_logging,
    ensure_dir,
    normalize_columns,
    write_dataframe,
)

REQUIRED_RAW_TABLES = {
    "olist_customers_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
}


def run_ingestion(
    raw_dir: Path,
    bronze_dir: Path,
    *,
    run_context: RunContext | None = None,
) -> list[Path]:
    ensure_dir(bronze_dir)
    csv_files = sorted(raw_dir.glob("*.csv"))
    if not csv_files:
        LOGGER.warning("No CSV files found in %s", raw_dir)
        return []

    missing_recommended = sorted(REQUIRED_RAW_TABLES.difference({path.name for path in csv_files}))
    if missing_recommended:
        LOGGER.warning("Recommended raw tables not found: %s", ", ".join(missing_recommended))

    created_files: list[Path] = []
    ingestion_time = datetime.now(UTC).isoformat()

    for csv_path in csv_files:
        df = pd.read_csv(csv_path)
        if df.empty:
            LOGGER.warning("Skipping empty CSV file %s", csv_path.name)
            continue
        df.columns = normalize_columns(df.columns.tolist())
        df["ingestion_ts_utc"] = ingestion_time
        df["source_file"] = csv_path.name

        output_path = bronze_dir / csv_path.name
        created_files.append(
            write_dataframe(
                df,
                output_path,
                stage="ingestion",
                source_tables=[csv_path.name],
                run_context=run_context,
            )
        )
        LOGGER.info("Ingested %s -> %s (%d rows)", csv_path.name, output_path, len(df))

    return created_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ingestion pipeline (raw -> bronze).")
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--bronze-dir", type=Path, default=Path("data/bronze"))
    return parser.parse_args()


if __name__ == "__main__":
    configure_logging()
    args = parse_args()
    run_ingestion(args.raw_dir, args.bronze_dir)
