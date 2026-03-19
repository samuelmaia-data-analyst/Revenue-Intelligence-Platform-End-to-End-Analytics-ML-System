from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from scripts.export_partner_payload import build_partner_payload  # noqa: E402
from scripts.smoke_support import smoke_pipeline_run  # noqa: E402


def main() -> None:
    with smoke_pipeline_run("rip-partner-payload-smoke-") as cfg:
        payload = build_partner_payload(cfg.processed_dir)

        if not payload["top_channels"]:
            raise SystemExit("Partner payload smoke failed: top_channels is empty.")
        if not payload["top_customer_actions"]:
            raise SystemExit("Partner payload smoke failed: top_customer_actions is empty.")
        if "avg_ltv_cac_ratio" not in payload["executive_kpis"]:
            raise SystemExit("Partner payload smoke failed: executive KPI surface is incomplete.")

    print("Partner payload smoke check passed.")


if __name__ == "__main__":
    main()
