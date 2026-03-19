from __future__ import annotations

import json
import logging
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from src.config import PipelineConfig
from src.orchestration import run_pipeline


def build_smoke_config(project_root: Path, *, prefix: str = "rip-smoke-") -> PipelineConfig:
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


@contextmanager
def smoke_pipeline_run(prefix: str) -> Iterator[PipelineConfig]:
    temp_root = Path(tempfile.mkdtemp(prefix=prefix))
    try:
        cfg = build_smoke_config(temp_root, prefix=prefix)
        run_pipeline(cfg)
        yield cfg
    finally:
        logging.shutdown()
        shutil.rmtree(temp_root, ignore_errors=True)
