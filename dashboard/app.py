from __future__ import annotations

import streamlit as st

from dashboard.components import (
    filter_monthly_revenue,
    inject_global_styles,
    render_dashboard_source_notice,
    render_footer,
    render_hero,
    render_sidebar,
    render_workspace_strip,
)
from dashboard.content import get_labels
from dashboard.data_access import load_dashboard_data, resolve_dashboard_sources
from dashboard.views import render_overview


def main() -> None:
    st.set_page_config(
        page_title="Revenue Intelligence Platform",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_global_styles()

    labels = get_labels()
    st.title("")
    source_paths = resolve_dashboard_sources()

    if not (source_paths.gold_dir / "business_kpis.csv").exists():
        st.error(labels["gold_missing"])
        st.stop()

    try:
        with st.spinner(labels["loading"]):
            data = load_dashboard_data(
                str(source_paths.gold_dir),
                serving_db=str(source_paths.serving_db),
            )
    except Exception as error:  # pragma: no cover - UI safety path
        st.error(labels["load_error"])
        st.exception(error)
        st.stop()

    available_months = data.monthly_revenue["order_month"].tolist()
    start_month, end_month = render_sidebar(labels, available_months=available_months)
    if start_month and end_month and start_month > end_month:
        start_month, end_month = end_month, start_month

    monthly_view = filter_monthly_revenue(
        data.monthly_revenue,
        start_month=start_month,
        end_month=end_month,
    )
    active_months = int(monthly_view["order_month"].nunique()) if not monthly_view.empty else 0
    customer_count = int(data.customer_360["customer_id"].nunique())

    render_hero(
        labels,
        active_months=active_months,
        customer_count=customer_count,
    )
    render_workspace_strip(
        labels,
        page_title=labels["nav_overview"],
        page_copy=labels["metrics_copy"],
        source_label=(
            labels["source_mode_demo"] if source_paths.demo_active else labels["source_mode_live"]
        ),
        active_months=active_months,
        customer_count=customer_count,
    )
    render_dashboard_source_notice(
        labels,
        demo_active=source_paths.demo_active,
        demo_mode=source_paths.demo_mode,
    )
    render_overview(labels, data, monthly_view)
    render_footer(
        labels,
        gold_dir=source_paths.gold_dir,
        run_dir=source_paths.run_dir,
        demo_active=source_paths.demo_active,
    )


if __name__ == "__main__":
    main()
