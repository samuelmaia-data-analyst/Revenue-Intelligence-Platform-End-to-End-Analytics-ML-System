from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelineConfig:
    project_root: Path
    data_dir: Path
    raw_dir: Path
    bronze_dir: Path
    silver_dir: Path
    gold_dir: Path
    processed_dir: Path
    warehouse_dir: Path
    warehouse_db_path: Path
    semantic_metrics_path: Path
    warehouse_target: str
    warehouse_url: str | None
    alerts_output_path: Path
    approvals_output_path: Path
    seed: int
    log_level: str

    def ensure_directories(self) -> None:
        for directory in [
            self.data_dir,
            self.raw_dir,
            self.bronze_dir,
            self.silver_dir,
            self.gold_dir,
            self.processed_dir,
            self.warehouse_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls, project_root: Path | None = None) -> PipelineConfig:
        root = project_root or Path(__file__).resolve().parents[1]
        data_dir = Path(os.getenv("RIP_DATA_DIR", str(root / "data")))
        seed = int(os.getenv("RIP_SEED", "42"))
        log_level = os.getenv("RIP_LOG_LEVEL", "INFO").upper()
        return cls(
            project_root=root,
            data_dir=data_dir,
            raw_dir=data_dir / "raw",
            bronze_dir=data_dir / "bronze",
            silver_dir=data_dir / "silver",
            gold_dir=data_dir / "gold",
            processed_dir=data_dir / "processed",
            warehouse_dir=data_dir / "warehouse",
            warehouse_db_path=data_dir / "warehouse" / "revenue_intelligence.db",
            semantic_metrics_path=root / "metrics" / "semantic_metrics.json",
            warehouse_target=os.getenv("RIP_WAREHOUSE_TARGET", "sqlite").strip().lower(),
            warehouse_url=os.getenv("RIP_WAREHOUSE_URL", "").strip() or None,
            alerts_output_path=data_dir / "processed" / "alerts_report.json",
            approvals_output_path=data_dir / "processed" / "approved_actions.csv",
            seed=seed,
            log_level=log_level,
        )
