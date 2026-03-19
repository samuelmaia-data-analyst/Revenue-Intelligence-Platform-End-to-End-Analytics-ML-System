from __future__ import annotations

import json
import logging
import shutil
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from scripts.export_partner_payload import build_partner_payload  # noqa: E402
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
    temp_root = Path(tempfile.mkdtemp(prefix="rip-partner-payload-smoke-"))
    try:
        cfg = _build_config(temp_root)
        run_pipeline(cfg)
        payload = build_partner_payload(cfg.processed_dir)

        if not payload["top_channels"]:
            raise SystemExit("Partner payload smoke failed: top_channels is empty.")
        if not payload["top_customer_actions"]:
            raise SystemExit("Partner payload smoke failed: top_customer_actions is empty.")
        if "avg_ltv_cac_ratio" not in payload["executive_kpis"]:
            raise SystemExit("Partner payload smoke failed: executive KPI surface is incomplete.")
    finally:
        logging.shutdown()
        shutil.rmtree(temp_root, ignore_errors=True)

    print("Partner payload smoke check passed.")


if __name__ == "__main__":
    main()
