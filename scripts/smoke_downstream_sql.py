from __future__ import annotations

import json
import logging
import shutil
import sqlite3
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
    temp_root = Path(tempfile.mkdtemp(prefix="rip-downstream-smoke-"))
    try:
        cfg = _build_config(temp_root)
        run_pipeline(cfg)

        expected_outcomes = json.loads(
            (cfg.processed_dir / "business_outcomes.json").read_text(encoding="utf-8")
        )
        with sqlite3.connect(cfg.warehouse_db_path) as connection:
            portfolio_semantic_query = pd.read_sql_query(
                """
                SELECT
                    SUM(scored.monetary) AS revenue_proxy,
                    AVG(recommendations.ltv_cac_ratio) AS avg_ltv_cac_ratio,
                    AVG(CASE WHEN recommendations.churn_probability >= 0.70 THEN 1.0 ELSE 0.0 END) AS high_churn_risk_pct
                FROM scored_customers scored
                INNER JOIN recommendations
                    ON scored.customer_id = recommendations.customer_id
                """,
                connection,
            )
            channel_query = pd.read_sql_query(
                """
                SELECT
                    recommendations.channel,
                    COUNT(*) AS customers_in_scope,
                    AVG(recommendations.ltv_cac_ratio) AS avg_ltv_cac_ratio
                FROM recommendations
                GROUP BY recommendations.channel
                ORDER BY recommendations.channel
                """,
                connection,
            )

        if portfolio_semantic_query.empty:
            raise SystemExit(
                "Downstream SQL smoke failed: portfolio semantic query returned no rows."
            )
        if channel_query.empty:
            raise SystemExit("Downstream SQL smoke failed: channel query returned no rows.")
        observed_ratio = float(portfolio_semantic_query.loc[0, "avg_ltv_cac_ratio"])
        expected_ratio = float(expected_outcomes["kpis"]["avg_ltv_cac_ratio"])
        if abs(observed_ratio - expected_ratio) >= 1e-9:
            raise SystemExit(
                "Downstream SQL smoke failed: warehouse semantic query diverged from business outcomes."
            )
        if not (channel_query["customers_in_scope"] > 0).all():
            raise SystemExit(
                "Downstream SQL smoke failed: channel query returned non-positive scope counts."
            )
    finally:
        logging.shutdown()
        shutil.rmtree(temp_root, ignore_errors=True)

    print("Downstream SQL smoke check passed.")


if __name__ == "__main__":
    main()
