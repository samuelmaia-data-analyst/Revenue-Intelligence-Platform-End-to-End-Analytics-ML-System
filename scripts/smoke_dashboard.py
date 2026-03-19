from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app.dashboard_data import filter_recommendations, load_processed_assets  # noqa: E402
from app.dashboard_i18n import EN_I18N, PT_BR_I18N, PT_PT_I18N  # noqa: E402
from app.dashboard_metrics import potential_impact  # noqa: E402
from app.views import dashboard_views  # noqa: E402


def main() -> None:
    processed_dir = PROJECT_ROOT / "data" / "processed"
    assets = load_processed_assets(str(processed_dir))
    recommendations = assets["recommendations"]
    if recommendations.empty:
        raise SystemExit("Dashboard smoke failed: recommendations.csv is empty.")

    filtered = filter_recommendations(
        recommendations,
        segment="__all__",
        channel="__all__",
        action="__all__",
        all_segments_label="__all__",
        all_channels_label="__all__",
        all_actions_label="__all__",
        potential_impact_fn=potential_impact,
    )
    if filtered.empty or "potential_impact" not in filtered.columns:
        raise SystemExit("Dashboard smoke failed: filtered recommendations are invalid.")

    import app.streamlit_app as streamlit_app  # noqa: F401

    required_keys = {
        "recommendations",
        "cohort",
        "unit",
        "top10",
        "report",
        "outcomes",
        "monitoring",
        "semantic_metrics",
        "alerts",
        "manifest",
        "artifact_validation",
        "freshness",
        "approved_actions",
    }
    missing_keys = sorted(required_keys.difference(assets))
    if missing_keys:
        raise SystemExit(f"Dashboard smoke failed: missing asset keys {missing_keys}.")

    required_view_functions = {
        "build_sidebar",
        "render_header",
        "render_filter_summary",
        "render_summary",
        "render_leadership_notes",
        "render_overview_tab",
        "render_risk_tab",
        "render_action_tab",
        "render_business_tab",
        "render_dashboard_footer",
    }
    missing_functions = sorted(
        name for name in required_view_functions if not hasattr(dashboard_views, name)
    )
    if missing_functions:
        raise SystemExit(
            f"Dashboard smoke failed: missing dashboard view functions {missing_functions}."
        )

    critical_i18n_keys = {
        "page_title",
        "header_title",
        "runtime_health",
        "tab_overview",
        "tab_risk_growth",
        "tab_action_list",
        "tab_business",
    }
    for lang_name, dictionary in {
        "pt-br": PT_BR_I18N,
        "pt-pt": PT_PT_I18N,
        "en": EN_I18N,
    }.items():
        missing_lang_keys = sorted(critical_i18n_keys.difference(dictionary))
        if missing_lang_keys:
            raise SystemExit(
                f"Dashboard smoke failed: missing i18n keys for {lang_name}: {missing_lang_keys}."
            )

    print("Dashboard smoke check passed.")


if __name__ == "__main__":
    main()
