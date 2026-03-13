from pathlib import Path

from src.config import PipelineConfig
from src.orchestration import run_pipeline


if __name__ == "__main__":
    config = PipelineConfig.from_env(Path(__file__).resolve().parent)
    run_pipeline(config)
