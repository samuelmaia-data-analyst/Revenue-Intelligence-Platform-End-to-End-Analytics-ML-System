from __future__ import annotations

from pathlib import Path

from src.config import PipelineConfig
from src.orchestration import run_pipeline

try:
    from prefect import flow, task
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    flow = None
    task = None


def _ensure_prefect_installed() -> None:
    if flow is None or task is None:
        raise RuntimeError(
            "Prefect is not installed. Add it to the environment to run scheduled orchestration."
        )


def build_prefect_flow():
    _ensure_prefect_installed()

    @task(name="resolve-config")
    def resolve_config(project_root: str | None = None) -> PipelineConfig:
        root = Path(project_root) if project_root else None
        return PipelineConfig.from_env(root)

    @task(name="run-revenue-intelligence-pipeline")
    def execute_pipeline(cfg: PipelineConfig) -> None:
        run_pipeline(cfg)

    @flow(name="revenue-intelligence-platform")
    def revenue_intelligence_flow(project_root: str | None = None) -> None:
        cfg = resolve_config(project_root)
        execute_pipeline(cfg)

    return revenue_intelligence_flow


def run_prefect_flow(project_root: str | None = None) -> None:
    flow_fn = build_prefect_flow()
    flow_fn(project_root=project_root)
