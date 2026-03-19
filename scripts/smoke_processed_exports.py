from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from scripts.smoke_support import smoke_pipeline_run  # noqa: E402


def main() -> None:
    with smoke_pipeline_run("rip-exports-smoke-") as cfg:
        outcomes = json.loads(
            (cfg.processed_dir / "business_outcomes.json").read_text(encoding="utf-8")
        )
        recommendations = pd.read_csv(cfg.processed_dir / "recommendations.csv")
        top_actions = pd.read_csv(cfg.processed_dir / "top_10_actions.csv")
        channel_cac = pd.read_csv(cfg.processed_dir / "cac_by_channel.csv")
        unit_economics = pd.read_csv(cfg.processed_dir / "unit_economics.csv")

        if recommendations.empty:
            raise SystemExit("Processed exports smoke failed: recommendations.csv is empty.")
        if top_actions.empty:
            raise SystemExit("Processed exports smoke failed: top_10_actions.csv is empty.")
        if channel_cac.empty:
            raise SystemExit("Processed exports smoke failed: cac_by_channel.csv is empty.")
        if unit_economics.empty:
            raise SystemExit("Processed exports smoke failed: unit_economics.csv is empty.")

        if "recommended_action" not in recommendations.columns:
            raise SystemExit(
                "Processed exports smoke failed: recommendations.csv is missing recommended_action."
            )

        if not recommendations["recommended_action"].notna().all():
            raise SystemExit(
                "Processed exports smoke failed: recommendations.csv contains null recommended_action values."
            )

        top_actions_from_outcomes = [
            str(action["customer_id"]) for action in outcomes["top_10_actions"]
        ]
        top_actions_export = top_actions["customer_id"].astype(str).tolist()
        if top_actions_from_outcomes != top_actions_export:
            raise SystemExit(
                "Processed exports smoke failed: top_10_actions.csv diverged from business outcomes."
            )

        observed_best_channel = unit_economics.sort_values("ltv_cac_ratio", ascending=False).iloc[
            0
        ]["channel"]
        expected_best_channel = max(
            outcomes["ltv_cac_by_channel"],
            key=lambda item: item["ltv_cac_ratio"],
        )["channel"]
        if str(observed_best_channel) != str(expected_best_channel):
            raise SystemExit(
                "Processed exports smoke failed: best channel in export does not match business outcomes."
            )

    print("Processed exports smoke check passed.")


if __name__ == "__main__":
    main()
