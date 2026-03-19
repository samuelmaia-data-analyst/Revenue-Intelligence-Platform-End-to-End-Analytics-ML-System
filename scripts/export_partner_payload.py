from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


def build_partner_payload(processed_dir: Path) -> dict[str, object]:
    outcomes = json.loads((processed_dir / "business_outcomes.json").read_text(encoding="utf-8"))
    top_actions = pd.read_csv(processed_dir / "top_10_actions.csv")
    unit_economics = pd.read_csv(processed_dir / "unit_economics.csv")

    top_channels = (
        unit_economics.sort_values("ltv_cac_ratio", ascending=False)
        .head(3)[["channel", "ltv_cac_ratio", "cac", "payback_period_months"]]
        .to_dict(orient="records")
    )
    top_customers = top_actions.head(5)[
        [
            "priority_rank",
            "customer_id",
            "channel",
            "segment",
            "action",
            "net_impact",
            "roi_simulated",
        ]
    ].to_dict(orient="records")

    return {
        "generated_from": str(processed_dir),
        "data_refresh_utc": outcomes["data_refresh_utc"],
        "executive_kpis": outcomes["kpis"],
        "top_channels": top_channels,
        "top_customer_actions": top_customers,
    }


def main() -> None:
    processed_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/processed")
    payload = build_partner_payload(processed_dir)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
