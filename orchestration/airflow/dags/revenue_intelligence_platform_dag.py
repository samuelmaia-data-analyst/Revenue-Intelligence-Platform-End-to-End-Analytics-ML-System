from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.config import PipelineConfig  # noqa: E402
from src.orchestration import run_pipeline  # noqa: E402


def execute_pipeline() -> None:
    cfg = PipelineConfig.from_env(PROJECT_ROOT)
    run_pipeline(cfg)


with DAG(
    dag_id="revenue_intelligence_platform",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["revenue-intelligence", "analytics", "ml"],
) as dag:
    pipeline_task = PythonOperator(
        task_id="run_revenue_intelligence_pipeline",
        python_callable=execute_pipeline,
    )

    pipeline_task
