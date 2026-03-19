from __future__ import annotations

import argparse

from analytics.health_checks import evaluate_platform_health
from models.churn_model import train_churn_model
from models.revenue_forecasting import forecast_revenue
from pipelines.bootstrap_sample_data import write_sample_raw_data
from pipelines.common import (
    LOGGER,
    build_run_context,
    configure_logging,
    snapshot_stage_artifacts,
    write_run_manifest,
)
from pipelines.feature_pipeline import run_feature_engineering
from pipelines.ingestion_pipeline import run_ingestion
from pipelines.transformation_pipeline import run_transformation
from ridp.config import get_runtime_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Revenue Intelligence Data Platform CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "bootstrap-sample-data", help="Create a minimal raw dataset for local demos."
    )

    pipeline_parser = subparsers.add_parser(
        "run-pipeline", help="Run one pipeline stage or the full flow."
    )
    pipeline_parser.add_argument(
        "stage",
        choices=["ingestion", "transformation", "features", "all"],
        help="Pipeline stage to run.",
    )
    pipeline_parser.add_argument(
        "--run-id",
        help="Optional execution identifier used in dataset metadata and run manifests.",
    )

    model_parser = subparsers.add_parser("train-model", help="Train one model artifact.")
    model_parser.add_argument("model", choices=["churn", "revenue"])
    model_parser.add_argument(
        "--periods",
        type=int,
        default=3,
        help="Forecast horizon in months.",
    )

    health_parser = subparsers.add_parser(
        "check-health",
        help="Validate freshness and operational readiness of curated platform artifacts.",
    )
    health_parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings as well as hard failures.",
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = get_runtime_settings()
    dirs = settings.directories
    configure_logging(settings.log_level)
    LOGGER.info("Starting command=%s", args.command)

    if args.command == "bootstrap-sample-data":
        write_sample_raw_data(dirs.raw)
        LOGGER.info("Sample data written to %s", dirs.raw)
        return

    if args.command == "run-pipeline":
        run_context = build_run_context(args.run_id)
        artifacts: dict[str, list[str]] = {}
        artifact_snapshots: dict[str, list[str]] = {}
        snapshot_root = dirs.run_artifacts / run_context.run_id
        if args.stage in {"ingestion", "all"}:
            artifacts["ingestion"] = [
                str(path) for path in run_ingestion(dirs.raw, dirs.bronze, run_context=run_context)
            ]
            artifact_snapshots["ingestion"] = snapshot_stage_artifacts(
                snapshot_root,
                stage="ingestion",
                artifact_paths=artifacts["ingestion"],
            )
        if args.stage in {"transformation", "all"}:
            artifacts["transformation"] = [
                str(path)
                for path in run_transformation(
                    dirs.bronze,
                    dirs.silver,
                    run_context=run_context,
                ).values()
            ]
            artifact_snapshots["transformation"] = snapshot_stage_artifacts(
                snapshot_root,
                stage="transformation",
                artifact_paths=artifacts["transformation"],
            )
        if args.stage in {"features", "all"}:
            artifacts["feature_engineering"] = [
                str(path)
                for path in run_feature_engineering(
                    dirs.silver,
                    dirs.gold,
                    run_context=run_context,
                    serving_db_path=dirs.serving,
                ).values()
            ]
            artifact_snapshots["feature_engineering"] = snapshot_stage_artifacts(
                snapshot_root,
                stage="feature_engineering",
                artifact_paths=artifacts["feature_engineering"],
            )
        manifest_path = write_run_manifest(
            dirs.runs,
            command="run-pipeline",
            stage=args.stage,
            run_context=run_context,
            artifacts=artifacts,
            artifact_snapshots=artifact_snapshots,
            snapshot_root=str(snapshot_root),
            history_db_path=dirs.run_history_db,
        )
        LOGGER.info("Pipeline stage completed: %s | run_id=%s", args.stage, run_context.run_id)
        LOGGER.info("Run manifest written to %s", manifest_path)
        return

    if args.command == "check-health":
        report = evaluate_platform_health(
            dirs,
            freshness_sla_hours=settings.freshness_sla_hours,
        )
        if report.checks.empty:
            LOGGER.warning("No health checks were generated.")
            return
        for row in report.checks.to_dict(orient="records"):
            LOGGER.info(
                "health_check=%s | target=%s | status=%s | detail=%s",
                row["check_name"],
                row["target"],
                row["status"],
                row["detail"],
            )
        should_fail = not report.failed.empty or (args.strict and not report.warnings.empty)
        if should_fail:
            raise SystemExit(1)
        return

    if args.command == "train-model":
        if args.model == "churn":
            train_churn_model(dirs.gold, dirs.models)
            LOGGER.info("Model training completed: churn")
            return
        forecast_revenue(dirs.gold, dirs.models, periods=args.periods)
        LOGGER.info("Model training completed: revenue")
        return

    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
