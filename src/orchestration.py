from __future__ import annotations

import json
import logging
import shutil
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import pandas as pd

from src.analytics import build_analytics_outputs
from src.config import PipelineConfig
from src.exceptions import PipelineStageError
from src.ingestion import build_bronze_layer, save_raw_datasets
from src.logging_utils import configure_logging
from src.monitoring import build_monitoring_report
from src.modeling import train_and_score_models
from src.persistence import persist_frames_to_sqlite
from src.quality import (
    build_dataset_quality_report,
    enforce_quality_gate,
    validate_required_columns,
    write_quality_report,
)
from src.reporting import build_business_outcomes, build_executive_report, build_executive_summary
from src.semantic_metrics import build_metric_catalog
from src.transformation import build_customer_features, build_silver_layer
from src.warehouse import build_star_schema

LOGGER = logging.getLogger("revenue_intelligence.pipeline")


def _copy_gold_outputs(cfg: PipelineConfig) -> None:
    for table in ["dim_customers.csv", "dim_date.csv", "dim_channel.csv", "fact_orders.csv"]:
        shutil.copy2(cfg.gold_dir / table, cfg.processed_dir / table)


def _write_manifest(cfg: PipelineConfig, stage_timings: dict[str, float], outputs: list[str]) -> dict:
    manifest = {
        "pipeline_name": "revenue_intelligence_platform",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "seed": cfg.seed,
        "data_dir": str(cfg.data_dir),
        "layers": {
            "raw": str(cfg.raw_dir),
            "bronze": str(cfg.bronze_dir),
            "silver": str(cfg.silver_dir),
            "gold": str(cfg.gold_dir),
            "processed": str(cfg.processed_dir),
            "warehouse": str(cfg.warehouse_db_path),
        },
        "stage_timings_seconds": {name: round(value, 3) for name, value in stage_timings.items()},
        "outputs": outputs,
    }
    with (cfg.processed_dir / "pipeline_manifest.json").open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2)
    return manifest


def _run_stage(stage_name: str, func):
    start = perf_counter()
    try:
        result = func()
    except Exception as exc:  # pragma: no cover - exercised in runtime failures
        raise PipelineStageError(f"Stage '{stage_name}' failed: {exc}") from exc
    return result, perf_counter() - start


def run_pipeline(cfg: PipelineConfig) -> None:
    configure_logging(cfg.log_level)
    cfg.ensure_directories()
    LOGGER.info("Pipeline started | data_dir=%s | seed=%s", cfg.data_dir, cfg.seed)

    stage_timings: dict[str, float] = {}

    (raw_paths, elapsed) = _run_stage(
        "ingestion.raw",
        lambda: save_raw_datasets(cfg.raw_dir, seed=cfg.seed),
    )
    stage_timings["ingestion.raw"] = elapsed
    customers_path, orders_path, marketing_path = raw_paths

    (bronze_paths, elapsed) = _run_stage(
        "ingestion.bronze",
        lambda: build_bronze_layer(customers_path, orders_path, marketing_path, cfg.bronze_dir),
    )
    stage_timings["ingestion.bronze"] = elapsed
    bronze_customers, bronze_orders, bronze_marketing = bronze_paths

    (silver_paths, elapsed) = _run_stage(
        "transformation.silver",
        lambda: build_silver_layer(bronze_customers, bronze_orders, bronze_marketing, cfg.silver_dir),
    )
    stage_timings["transformation.silver"] = elapsed
    silver_customers, silver_orders, silver_marketing = silver_paths

    customers_df = pd.read_csv(silver_customers, parse_dates=["signup_date"])
    orders_df = pd.read_csv(silver_orders, parse_dates=["order_date"])
    marketing_df = pd.read_csv(silver_marketing)

    validate_required_columns(customers_df, {"customer_id", "signup_date", "channel", "segment"}, "silver_customers")
    validate_required_columns(orders_df, {"order_id", "customer_id", "order_date", "order_value"}, "silver_orders")
    validate_required_columns(marketing_df, {"channel", "marketing_spend"}, "silver_marketing")
    quality_reports = [
        build_dataset_quality_report(customers_df, "silver_customers", primary_key="customer_id"),
        build_dataset_quality_report(
            orders_df,
            "silver_orders",
            primary_key="order_id",
            foreign_key="customer_id",
            valid_values=set(customers_df["customer_id"].tolist()),
        ),
        build_dataset_quality_report(marketing_df, "silver_marketing", primary_key="channel"),
    ]
    enforce_quality_gate(quality_reports)
    write_quality_report(quality_reports, cfg.processed_dir / "quality_report.json")

    (features_df, elapsed) = _run_stage(
        "transformation.features",
        lambda: build_customer_features(silver_customers, silver_orders, cfg.processed_dir),
    )
    stage_timings["transformation.features"] = elapsed

    (_, elapsed) = _run_stage(
        "warehouse.gold",
        lambda: build_star_schema(silver_customers, silver_orders, cfg.gold_dir),
    )
    stage_timings["warehouse.gold"] = elapsed
    _copy_gold_outputs(cfg)

    ((churn_results, next_purchase_results, scored_df), elapsed) = _run_stage(
        "ml.training",
        lambda: train_and_score_models(features_df, cfg.processed_dir),
    )
    stage_timings["ml.training"] = elapsed

    (analytics_outputs, elapsed) = _run_stage(
        "analytics.metrics",
        lambda: build_analytics_outputs(
            scored_df=scored_df,
            silver_customers_path=silver_customers,
            silver_orders_path=silver_orders,
            silver_marketing_path=silver_marketing,
            processed_dir=cfg.processed_dir,
        ),
    )
    stage_timings["analytics.metrics"] = elapsed

    recommendations_df = analytics_outputs["recommendations"]
    unit_df = analytics_outputs["unit_economics"]
    kpi_snapshot = analytics_outputs["kpi_snapshot"]

    (_, elapsed) = _run_stage(
        "governance.semantic_metrics",
        lambda: build_metric_catalog(
            cfg.semantic_metrics_path,
            cfg.processed_dir / "semantic_metrics_catalog.json",
        ),
    )
    stage_timings["governance.semantic_metrics"] = elapsed

    (_, elapsed) = _run_stage(
        "monitoring.model",
        lambda: build_monitoring_report(
            scored_df=scored_df,
            labeled_df=scored_df,
            output_path=cfg.processed_dir / "monitoring_report.json",
            baseline_path=cfg.processed_dir / "monitoring_baseline.json",
        ),
    )
    stage_timings["monitoring.model"] = elapsed

    (_, elapsed) = _run_stage(
        "insights.reporting",
        lambda: (
            build_executive_report(
                recommendations_df=recommendations_df,
                churn_results=churn_results,
                next_purchase_results=next_purchase_results,
                kpi_snapshot=kpi_snapshot,
                output_path=cfg.processed_dir / "executive_report.json",
            ),
            build_executive_summary(
                recommendations_df=recommendations_df,
                scored_df=scored_df,
                unit_economics_df=unit_df,
                kpi_snapshot=kpi_snapshot,
                output_path=cfg.processed_dir / "executive_summary.json",
            ),
            build_business_outcomes(
                recommendations_df=recommendations_df,
                unit_economics_df=unit_df,
                outcomes_path=cfg.processed_dir / "business_outcomes.json",
                top_actions_path=cfg.processed_dir / "top_10_actions.csv",
            ),
        ),
    )
    stage_timings["insights.reporting"] = elapsed

    warehouse_frames = {
        "dim_customers": pd.read_csv(cfg.processed_dir / "dim_customers.csv"),
        "dim_date": pd.read_csv(cfg.processed_dir / "dim_date.csv"),
        "dim_channel": pd.read_csv(cfg.processed_dir / "dim_channel.csv"),
        "fact_orders": pd.read_csv(cfg.processed_dir / "fact_orders.csv"),
        "customer_features": pd.read_csv(cfg.processed_dir / "customer_features.csv"),
        "scored_customers": pd.read_csv(cfg.processed_dir / "scored_customers.csv"),
        "recommendations": pd.read_csv(cfg.processed_dir / "recommendations.csv"),
        "unit_economics": pd.read_csv(cfg.processed_dir / "unit_economics.csv"),
        "top_10_actions": pd.read_csv(cfg.processed_dir / "top_10_actions.csv"),
    }
    (_, elapsed) = _run_stage(
        "warehouse.sqlite",
        lambda: persist_frames_to_sqlite(warehouse_frames, cfg.warehouse_db_path),
    )
    stage_timings["warehouse.sqlite"] = elapsed

    manifest = _write_manifest(
        cfg,
        stage_timings=stage_timings,
        outputs=sorted(
            set(path.name for path in cfg.processed_dir.glob("*") if path.is_file())
            | {cfg.warehouse_db_path.name}
        ),
    )
    LOGGER.info("Pipeline completed successfully | outputs=%s", len(manifest["outputs"]))
