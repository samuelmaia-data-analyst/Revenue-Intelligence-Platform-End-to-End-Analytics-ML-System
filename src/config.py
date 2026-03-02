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
    seed: int
    log_level: str

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
            seed=seed,
            log_level=log_level,
        )
