from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(18, 95, 110, 0.10), transparent 28%),
                linear-gradient(180deg, #f4f7fb 0%, #eef2f7 100%);
            color: #102033;
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2.5rem;
            max-width: 1200px;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #16213b 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }
        [data-testid="stSidebar"] * {
            color: #e5eefb;
        }
        .hero-card {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 58%, #0f766e 100%);
            padding: 1.5rem 1.6rem;
            border-radius: 24px;
            color: #f8fbff;
            box-shadow: 0 20px 45px rgba(15, 23, 42, 0.16);
            margin-bottom: 1rem;
        }
        .hero-kicker {
            letter-spacing: 0.12em;
            text-transform: uppercase;
            font-size: 0.72rem;
            opacity: 0.72;
            margin-bottom: 0.45rem;
        }
        .hero-title {
            font-size: 2.1rem;
            font-weight: 700;
            margin: 0;
        }
        .hero-copy {
            margin-top: 0.65rem;
            line-height: 1.5;
            max-width: 60rem;
            opacity: 0.92;
        }
        .section-label {
            font-size: 0.76rem;
            letter-spacing: 0.10em;
            text-transform: uppercase;
            color: #4b5563;
            margin-bottom: 0.4rem;
        }
        .section-title {
            font-size: 1.35rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.25rem;
        }
        .section-copy {
            color: #526072;
            margin-bottom: 1rem;
        }
        .metric-card {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 20px;
            padding: 1rem 1rem 0.9rem 1rem;
            box-shadow: 0 10px 30px rgba(148, 163, 184, 0.18);
            min-height: 136px;
        }
        .metric-label {
            color: #64748b;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.45rem;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.35rem;
        }
        .metric-caption {
            color: #475569;
            font-size: 0.9rem;
        }
        .metric-delta {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            margin-top: 0.55rem;
            padding: 0.28rem 0.55rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 600;
            background: rgba(15, 118, 110, 0.10);
            color: #0f766e;
        }
        .metric-delta.down {
            background: rgba(220, 38, 38, 0.10);
            color: #b91c1c;
        }
        .metric-delta.neutral {
            background: rgba(71, 85, 105, 0.10);
            color: #475569;
        }
        .status-card {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 18px;
            padding: 0.95rem 1rem;
            box-shadow: 0 10px 26px rgba(148, 163, 184, 0.12);
        }
        .status-label {
            color: #64748b;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .status-value {
            margin-top: 0.35rem;
            color: #0f172a;
            font-size: 1.15rem;
            font-weight: 700;
        }
        .status-copy {
            margin-top: 0.35rem;
            color: #526072;
            font-size: 0.88rem;
        }
        .panel-card {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 22px;
            padding: 1rem 1.1rem 1.1rem 1.1rem;
            box-shadow: 0 10px 30px rgba(148, 163, 184, 0.14);
        }
        .footer-card {
            margin-top: 1rem;
            padding: 1rem 1.2rem;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid rgba(15, 23, 42, 0.08);
            color: #526072;
            font-size: 0.92rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(
    labels: dict[str, str],
    *,
    available_months: list[str],
) -> tuple[str | None, str | None]:
    st.sidebar.selectbox(
        "Language / Idioma",
        options=["English", "Portuguese", "Spanish"],
        key="dashboard_language",
    )
    st.sidebar.markdown("## Revenue Intelligence")
    st.sidebar.caption(labels["sidebar_caption"])
    source_mode_options = {
        labels["source_mode_auto"]: "AUTO",
        labels["source_mode_live"]: "OFF",
        labels["source_mode_demo"]: "ON",
    }
    current_mode = st.session_state.get("dashboard_source_mode", "AUTO")
    selected_source_label = next(
        (label for label, value in source_mode_options.items() if value == current_mode),
        labels["source_mode_auto"],
    )
    selected_source = st.sidebar.selectbox(
        labels["source_mode_title"],
        options=list(source_mode_options.keys()),
        index=list(source_mode_options.keys()).index(selected_source_label),
    )
    st.session_state["dashboard_source_mode"] = source_mode_options[selected_source]
    st.sidebar.caption(labels["source_mode_copy"])
    st.sidebar.divider()
    st.sidebar.markdown(f"### {labels['nav_title']}")
    if hasattr(st, "page_link"):
        st.sidebar.page_link("app.py", label=labels["nav_overview"])
        st.sidebar.page_link("pages/01_Customer_Health.py", label=labels["nav_customers"])
        st.sidebar.page_link("pages/02_Operations.py", label=labels["nav_operations"])
        st.sidebar.page_link("pages/03_Run_History.py", label=labels["nav_run_history"])
    st.sidebar.divider()
    st.sidebar.markdown(f"### {labels['filters_title']}")
    if available_months:
        start_month = st.sidebar.selectbox(
            labels["start_month"],
            options=available_months,
            index=0,
        )
        end_month = st.sidebar.selectbox(
            labels["end_month"],
            options=available_months,
            index=len(available_months) - 1,
        )
    else:
        st.sidebar.caption(labels["no_months"])
        start_month = None
        end_month = None
    st.sidebar.divider()
    with st.sidebar.expander(labels["sidebar_help"], expanded=False):
        st.markdown(labels["sidebar_help_copy"])
    return start_month, end_month


def render_hero(labels: dict[str, str], *, active_months: int, customer_count: int) -> None:
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-kicker">{labels["hero_kicker"]}</div>
            <h1 class="hero-title">{labels["title"]}</h1>
            <div class="hero-copy">
                {labels["caption"]}<br/>
                {
                    labels["hero_summary"].format(
                        active_months=active_months,
                        customer_count=customer_count,
                    )
                }
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_intro(label: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="section-label">{label}</div>
        <div class="section-title">{title}</div>
        <div class="section-copy">{copy}</div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(title: str, value: str, caption: str) -> None:
    render_metric_card_with_delta(title, value, caption)


def render_metric_card_with_delta(
    title: str,
    value: str,
    caption: str,
    *,
    delta_text: str | None = None,
    delta_state: str = "neutral",
) -> None:
    delta_html = ""
    if delta_text:
        delta_html = f'<div class="metric-delta {delta_state}">{delta_text}</div>'
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-caption">{caption}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(title: str, body: str) -> None:
    st.info(f"**{title}**\n\n{body}")


def render_dashboard_source_notice(
    labels: dict[str, str],
    *,
    demo_active: bool,
    demo_mode: str,
) -> None:
    if not demo_active:
        return
    st.info(
        labels["demo_banner_copy"].format(
            demo_mode=demo_mode,
        )
    )


def render_footer(
    labels: dict[str, str],
    *,
    gold_dir: Path,
    run_dir: Path,
    demo_active: bool,
) -> None:
    st.markdown(
        f"""
        <div class="footer-card">
            <strong>{labels["footer_title"]}</strong><br/>
            {
                labels["footer_copy"].format(
                    gold_dir=gold_dir,
                    run_dir=run_dir,
                    source_mode=("demo" if demo_active else "primary"),
                )
            }
        </div>
        """,
        unsafe_allow_html=True,
    )


def filter_monthly_revenue(
    monthly_revenue: pd.DataFrame,
    *,
    start_month: str | None,
    end_month: str | None,
) -> pd.DataFrame:
    if monthly_revenue.empty or start_month is None or end_month is None:
        return monthly_revenue

    return monthly_revenue[
        (monthly_revenue["order_month"] >= start_month)
        & (monthly_revenue["order_month"] <= end_month)
    ].copy()


def read_metadata_file(metadata_path: Path) -> dict[str, str | int | None]:
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def render_status_card(title: str, value: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-label">{title}</div>
            <div class="status-value">{value}</div>
            <div class="status-copy">{copy}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
