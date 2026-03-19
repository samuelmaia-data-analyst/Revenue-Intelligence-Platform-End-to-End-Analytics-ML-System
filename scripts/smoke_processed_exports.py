from __future__ import annotations

import json
import logging
import shutil
import sys
import tempfile
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.config import PipelineConfig  # noqa: E402
from src.orchestration import run_pipeline  # noqa: E402


def _build_config(project_root: Path) -> PipelineConfig:
    data_dir = project_root / "data"
    metrics_path = project_root / "metrics" / "semantic_metrics.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(
        json.dumps(
            {
                "version": "1.0",
                "metrics": [{"name": "revenue_proxy", "expression": "sum(monetary)"}],
            }
        ),
        encoding="utf-8",
    )
    return PipelineConfig(
        project_root=project_root,
        data_dir=data_dir,
        raw_dir=data_dir / "raw",
        bronze_dir=data_dir / "bronze",
        silver_dir=data_dir / "silver",
        gold_dir=data_dir / "gold",
        processed_dir=data_dir / "processed",
        warehouse_dir=data_dir / "warehouse",
        warehouse_db_path=data_dir / "warehouse" / "revenue_intelligence.db",
        semantic_metrics_path=metrics_path,
        alerts_output_path=data_dir / "processed" / "alerts_report.json",
        approvals_output_path=data_dir / "processed" / "approved_actions.csv",
        runs_dir=data_dir / "runs",
        manifests_dir=data_dir / "manifests",
        snapshots_dir=data_dir / "snapshots",
        data_dictionary_path=data_dir / "processed" / "data_dictionary.json",
        env_name="smoke",
        warehouse_target="sqlite",
        warehouse_url=None,
        seed=42,
        log_level="WARNING",
        freshness_max_age_hours=48,
        snapshot_retention_runs=2,
        snapshot_retention_days=30,
        failure_retention_days=14,
    )


def main() -> None:
    temp_root = Path(tempfile.mkdtemp(prefix="rip-exports-smoke-"))
    try:
        cfg = _build_config(temp_root)
        run_pipeline(cfg)

        outcomes = json.loads(
            (cfg.processed_dir / "business_outcomes.json").read_text(encoding="utf-8")
        )
        recommendations = pd.read_csv(cfg.processed_dir / "recommendations.csv")
        top_actions = pd.read_csv(cfg.processed_dir / "top_10_actions.csv")
        channel_cac = pd.read_csv(cfg.processed_dir / "cac_by_channel.csv")
        unit_economics = pd.read_csv(cfg.processed_dir / "unit_economics.csv")

        if recommendations.empty:
            raise SystemExit("Processed exports smoke failed: recommendations.csv is empty.")
        if top_actions.empty:
            raise SystemExit("Processed exports smoke failed: top_10_actions.csv is empty.")
        if channel_cac.empty:
            raise SystemExit("Processed exports smoke failed: cac_by_channel.csv is empty.")
        if unit_economics.empty:
            raise SystemExit("Processed exports smoke failed: unit_economics.csv is empty.")

        if "recommended_action" not in recommendations.columns:
            raise SystemExit(
                "Processed exports smoke failed: recommendations.csv is missing recommended_action."
            )

        if not recommendations["recommended_action"].notna().all():
            raise SystemExit(
                "Processed exports smoke failed: recommendations.csv contains null recommended_action values."
            )

        top_actions_from_outcomes = [
            str(action["customer_id"]) for action in outcomes["top_10_actions"]
        ]
        top_actions_export = top_actions["customer_id"].astype(str).tolist()
        if top_actions_from_outcomes != top_actions_export:
            raise SystemExit(
                "Processed exports smoke failed: top_10_actions.csv diverged from business outcomes."
            )

        observed_best_channel = unit_economics.sort_values("ltv_cac_ratio", ascending=False).iloc[
            0
        ]["channel"]
        expected_best_channel = max(
            outcomes["ltv_cac_by_channel"],
            key=lambda item: item["ltv_cac_ratio"],
        )["channel"]
        if str(observed_best_channel) != str(expected_best_channel):
            raise SystemExit(
                "Processed exports smoke failed: best channel in export does not match business outcomes."
            )
    finally:
        logging.shutdown()
        shutil.rmtree(temp_root, ignore_errors=True)

    print("Processed exports smoke check passed.")


if __name__ == "__main__":
    main()
