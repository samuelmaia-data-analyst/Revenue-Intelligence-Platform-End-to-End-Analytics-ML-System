from __future__ import annotations

import streamlit as st

from dashboard.components import (
    inject_global_styles,
    render_dashboard_source_notice,
    render_footer,
    render_hero,
    render_sidebar,
)
from dashboard.content import get_labels
from dashboard.data_access import load_dashboard_data, resolve_dashboard_sources
from dashboard.views import render_customer_health


def main() -> None:
    st.set_page_config(
        page_title="Customer Health",
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
            data = load_dashboard_data(str(source_paths.gold_dir))
    except Exception as error:  # pragma: no cover - UI safety path
        st.error(labels["load_error"])
        st.exception(error)
        st.stop()

    render_sidebar(labels, available_months=data.monthly_revenue["order_month"].tolist())
    render_hero(
        labels,
        active_months=int(data.monthly_revenue["order_month"].nunique()),
        customer_count=int(data.customer_360["customer_id"].nunique()),
    )
    render_dashboard_source_notice(
        labels,
        demo_active=source_paths.demo_active,
        demo_mode=source_paths.demo_mode,
    )
    render_customer_health(labels, data.customer_360)
    render_footer(
        labels,
        gold_dir=source_paths.gold_dir,
        run_dir=source_paths.run_dir,
        demo_active=source_paths.demo_active,
    )


if __name__ == "__main__":
    main()
