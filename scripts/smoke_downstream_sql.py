from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from scripts.smoke_support import smoke_pipeline_run  # noqa: E402


def main() -> None:
    with smoke_pipeline_run("rip-downstream-smoke-") as cfg:
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

    print("Downstream SQL smoke check passed.")


if __name__ == "__main__":
    main()
