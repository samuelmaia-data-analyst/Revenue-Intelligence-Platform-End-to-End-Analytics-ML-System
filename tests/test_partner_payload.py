from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from scripts.export_partner_payload import build_partner_payload


def test_partner_payload_uses_governed_processed_exports(tmp_path: Path) -> None:
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    (processed_dir / "business_outcomes.json").write_text(
        json.dumps(
            {
                "data_refresh_utc": "2026-03-19T15:00:00+00:00",
                "kpis": {"avg_ltv_cac_ratio": 7.3, "high_churn_risk_pct": 0.05},
            }
        ),
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            {
                "priority_rank": 1,
                "customer_id": 101,
                "channel": "Referral",
                "segment": "Enterprise",
                "action": "Upsell Offer",
                "net_impact": 320.0,
                "roi_simulated": 1.7,
            },
            {
                "priority_rank": 2,
                "customer_id": 202,
                "channel": "Organic",
                "segment": "SMB",
                "action": "Retention Campaign",
                "net_impact": 210.0,
                "roi_simulated": 1.3,
            },
        ]
    ).to_csv(processed_dir / "top_10_actions.csv", index=False)
    pd.DataFrame(
        [
            {
                "channel": "Referral",
                "ltv_cac_ratio": 6.2,
                "cac": 55.0,
                "payback_period_months": 1.2,
            },
            {
                "channel": "Organic",
                "ltv_cac_ratio": 5.6,
                "cac": 70.0,
                "payback_period_months": 1.4,
            },
            {
                "channel": "Paid Search",
                "ltv_cac_ratio": 2.4,
                "cac": 180.0,
                "payback_period_months": 3.2,
            },
        ]
    ).to_csv(processed_dir / "unit_economics.csv", index=False)

    payload = build_partner_payload(processed_dir)

    assert payload["generated_from"] == str(processed_dir)
    assert payload["executive_kpis"]["avg_ltv_cac_ratio"] == 7.3
    assert payload["top_channels"][0]["channel"] == "Referral"
    assert payload["top_customer_actions"][0]["customer_id"] == 101
