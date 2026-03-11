from __future__ import annotations

import argparse

from models.churn_model import train_churn_model
from models.revenue_forecasting import forecast_revenue
from pipelines.bootstrap_sample_data import write_sample_raw_data
from pipelines.feature_pipeline import run_feature_engineering
from pipelines.ingestion_pipeline import run_ingestion
from pipelines.transformation_pipeline import run_transformation
from ridp.config import get_data_directories


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Revenue Intelligence Data Platform CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("bootstrap-sample-data", help="Create a minimal raw dataset for local demos.")

    pipeline_parser = subparsers.add_parser("run-pipeline", help="Run one pipeline stage or the full flow.")
    pipeline_parser.add_argument(
        "stage",
        choices=["ingestion", "transformation", "features", "all"],
        help="Pipeline stage to run.",
    )

    model_parser = subparsers.add_parser("train-model", help="Train one model artifact.")
    model_parser.add_argument("model", choices=["churn", "revenue"])
    model_parser.add_argument("--periods", type=int, default=3, help="Forecast horizon in months.")

    return parser


def main() -> None:
    args = build_parser().parse_args()
    dirs = get_data_directories()

    if args.command == "bootstrap-sample-data":
        write_sample_raw_data(dirs.raw)
        return

    if args.command == "run-pipeline":
        if args.stage in {"ingestion", "all"}:
            run_ingestion(dirs.raw, dirs.bronze)
        if args.stage in {"transformation", "all"}:
            run_transformation(dirs.bronze, dirs.silver)
        if args.stage in {"features", "all"}:
            run_feature_engineering(dirs.silver, dirs.gold)
        return

    if args.command == "train-model":
        if args.model == "churn":
            train_churn_model(dirs.gold, dirs.models)
            return
        forecast_revenue(dirs.gold, dirs.models, periods=args.periods)


if __name__ == "__main__":
    main()
