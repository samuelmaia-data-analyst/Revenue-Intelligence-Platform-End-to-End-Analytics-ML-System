from __future__ import annotations

from pathlib import Path

from src.config import PipelineConfig


def test_pipeline_config_uses_env_overrides(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RIP_DATA_DIR", str(tmp_path / "custom-data"))
    monkeypatch.setenv("RIP_SEED", "123")
    monkeypatch.setenv("RIP_LOG_LEVEL", "debug")

    cfg = PipelineConfig.from_env(project_root=tmp_path)

    assert cfg.data_dir == tmp_path / "custom-data"
    assert cfg.raw_dir == tmp_path / "custom-data" / "raw"
    assert cfg.seed == 123
    assert cfg.log_level == "DEBUG"
