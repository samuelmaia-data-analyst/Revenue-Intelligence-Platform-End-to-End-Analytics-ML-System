from __future__ import annotations

import html
import json
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ridp-slate-950: #0f172a;
            --ridp-slate-900: #16213b;
            --ridp-slate-700: #334155;
            --ridp-slate-500: #64748b;
            --ridp-slate-400: #94a3b8;
            --ridp-slate-200: #dbe4f0;
            --ridp-teal-700: #0f766e;
            --ridp-teal-500: #14b8a6;
            --ridp-blue-700: #1d4ed8;
            --ridp-amber-500: #f59e0b;
            --ridp-surface: rgba(255, 255, 255, 0.9);
        }
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
        .workspace-strip {
            display: grid;
            grid-template-columns: 1.35fr 1fr 1fr 1fr;
            gap: 0.85rem;
            margin: 0 0 1rem 0;
        }
        .workspace-panel {
            background: rgba(255, 255, 255, 0.74);
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 20px;
            padding: 1rem 1.05rem;
            box-shadow: 0 12px 34px rgba(148, 163, 184, 0.12);
            backdrop-filter: blur(8px);
        }
        .workspace-panel.primary {
            background: linear-gradient(
                180deg,
                rgba(255, 255, 255, 0.94),
                rgba(255, 255, 255, 0.82)
            );
        }
        .workspace-kicker {
            font-size: 0.72rem;
            letter-spacing: 0.11em;
            text-transform: uppercase;
            color: var(--ridp-slate-500);
            margin-bottom: 0.4rem;
        }
        .workspace-title {
            color: var(--ridp-slate-950);
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.18rem;
        }
        .workspace-copy {
            color: #526072;
            font-size: 0.92rem;
            line-height: 1.5;
        }
        .workspace-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.34rem 0.62rem;
            border-radius: 999px;
            background: rgba(15, 118, 110, 0.10);
            color: var(--ridp-teal-700);
            font-size: 0.8rem;
            font-weight: 600;
            margin-top: 0.6rem;
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
        .panel-title {
            color: var(--ridp-slate-950);
            font-size: 1.02rem;
            font-weight: 700;
            margin-bottom: 0.18rem;
        }
        .panel-copy {
            color: #526072;
            font-size: 0.89rem;
            margin-bottom: 0.9rem;
        }
        .state-card {
            border-radius: 20px;
            border: 1px dashed rgba(15, 23, 42, 0.14);
            background: rgba(255, 255, 255, 0.7);
            padding: 1rem 1.1rem;
            color: #334155;
            margin: 0.5rem 0 0.75rem 0;
        }
        .state-card strong {
            display: block;
            color: var(--ridp-slate-950);
            margin-bottom: 0.3rem;
        }
        .notice-card {
            border-radius: 18px;
            padding: 0.9rem 1rem;
            border: 1px solid rgba(245, 158, 11, 0.18);
            background: linear-gradient(
                90deg,
                rgba(255, 251, 235, 0.95),
                rgba(255, 255, 255, 0.88)
            );
            color: #78350f;
            margin-bottom: 1rem;
        }
        .table-card {
            border-radius: 20px;
            overflow: hidden;
            border: 1px solid rgba(15, 23, 42, 0.08);
            background: rgba(255, 255, 255, 0.88);
            box-shadow: 0 10px 28px rgba(148, 163, 184, 0.12);
        }
        .table-scroll {
            overflow-x: auto;
        }
        .table-grid {
            width: 100%;
            border-collapse: collapse;
        }
        .table-grid thead th {
            text-align: left;
            padding: 0.78rem 0.9rem;
            font-size: 0.74rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #64748b;
            background: rgba(248, 250, 252, 0.92);
            border-bottom: 1px solid rgba(15, 23, 42, 0.08);
        }
        .table-grid tbody td {
            padding: 0.82rem 0.9rem;
            font-size: 0.9rem;
            color: #1e293b;
            border-bottom: 1px solid rgba(226, 232, 240, 0.72);
            vertical-align: middle;
        }
        .table-grid tbody tr:last-child td {
            border-bottom: none;
        }
        .table-grid tbody tr:hover td {
            background: rgba(248, 250, 252, 0.72);
        }
        .table-chip {
            display: inline-flex;
            align-items: center;
            padding: 0.24rem 0.56rem;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }
        .table-chip.neutral {
            background: rgba(71, 85, 105, 0.12);
            color: #475569;
        }
        .table-chip.info {
            background: rgba(29, 78, 216, 0.10);
            color: #1d4ed8;
        }
        .table-chip.success {
            background: rgba(15, 118, 110, 0.10);
            color: #0f766e;
        }
        .table-chip.warning {
            background: rgba(245, 158, 11, 0.14);
            color: #92400e;
        }
        .table-chip.danger {
            background: rgba(220, 38, 38, 0.10);
            color: #b91c1c;
        }
        .table-muted {
            color: #64748b;
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
        @media (max-width: 980px) {
            .workspace-strip {
                grid-template-columns: 1fr;
            }
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
    hydrate_session_from_query_params(
        [
            "dashboard_language",
            "dashboard_source_mode",
            "dashboard_start_month",
            "dashboard_end_month",
        ]
    )
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
        current_start = st.session_state.get("dashboard_start_month")
        current_end = st.session_state.get("dashboard_end_month")
        start_index = (
            available_months.index(current_start)
            if isinstance(current_start, str) and current_start in available_months
            else 0
        )
        end_index = (
            available_months.index(current_end)
            if isinstance(current_end, str) and current_end in available_months
            else len(available_months) - 1
        )
        start_month = st.sidebar.selectbox(
            labels["start_month"],
            options=available_months,
            index=start_index,
            key="dashboard_start_month",
        )
        end_month = st.sidebar.selectbox(
            labels["end_month"],
            options=available_months,
            index=end_index,
            key="dashboard_end_month",
        )
    else:
        st.sidebar.caption(labels["no_months"])
        start_month = None
        end_month = None
    st.sidebar.divider()
    with st.sidebar.expander(labels["sidebar_help"], expanded=False):
        st.markdown(labels["sidebar_help_copy"])
    sync_query_params(
        [
            "dashboard_language",
            "dashboard_source_mode",
            "dashboard_start_month",
            "dashboard_end_month",
        ]
    )
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


def render_workspace_strip(
    labels: dict[str, str],
    *,
    page_title: str,
    page_copy: str,
    source_label: str,
    active_months: int,
    customer_count: int,
) -> None:
    st.markdown(
        f"""
        <div class="workspace-strip">
            <div class="workspace-panel primary">
                <div class="workspace-kicker">{labels["workspace_kicker"]}</div>
                <div class="workspace-title">{page_title}</div>
                <div class="workspace-copy">{page_copy}</div>
                <div class="workspace-chip">{labels["workspace_chip"]}</div>
            </div>
            <div class="workspace-panel">
                <div class="workspace-kicker">{labels["source_mode_title"]}</div>
                <div class="workspace-title">{source_label}</div>
                <div class="workspace-copy">{labels["workspace_source_copy"]}</div>
            </div>
            <div class="workspace-panel">
                <div class="workspace-kicker">{labels["workspace_periods_title"]}</div>
                <div class="workspace-title">{active_months:,}</div>
                <div class="workspace-copy">{labels["workspace_periods_copy"]}</div>
            </div>
            <div class="workspace-panel">
                <div class="workspace-kicker">{labels["workspace_customers_title"]}</div>
                <div class="workspace-title">{customer_count:,}</div>
                <div class="workspace-copy">{labels["workspace_customers_copy"]}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_panel_header(title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="panel-title">{title}</div>
        <div class="panel-copy">{copy}</div>
        """,
        unsafe_allow_html=True,
    )


def _normalize_query_value(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        return str(value[0]) if value else None
    return str(value)


def hydrate_session_from_query_params(keys: list[str]) -> None:
    query_params = getattr(st, "query_params", None)
    if query_params is None:
        return
    for key in keys:
        if key in st.session_state:
            continue
        value = _normalize_query_value(query_params.get(key))
        if value is not None:
            st.session_state[key] = value


def sync_query_params(keys: list[str]) -> None:
    query_params = getattr(st, "query_params", None)
    if query_params is None:
        return
    for key in keys:
        value = st.session_state.get(key)
        if value is None or value == "":
            if key in query_params:
                del query_params[key]
            continue
        query_params[key] = str(value)


def render_share_snapshot(
    labels: dict[str, str],
    *,
    state_keys: list[str],
    snapshot_name: str,
) -> None:
    sync_query_params(state_keys)
    snapshot = {
        key: str(value)
        for key, value in st.session_state.items()
        if key in state_keys and value not in (None, "")
    }
    if not snapshot:
        return
    query_string = "&".join(
        f"{quote(str(key))}={quote(str(value))}" for key, value in snapshot.items()
    )
    with st.expander(labels["share_state_title"], expanded=False):
        st.caption(labels["share_state_copy"])
        st.code(f"?{query_string}", language="text")
        st.download_button(
            labels["share_state_download"],
            data=json.dumps(snapshot, indent=2),
            file_name=f"{snapshot_name}_state.json",
            mime="application/json",
        )


def render_table_card(
    dataframe: pd.DataFrame,
    *,
    formatters: dict[str, str] | None = None,
    chip_columns: dict[str, dict[str, str]] | None = None,
    bar_columns: dict[str, float] | None = None,
) -> None:
    if dataframe.empty:
        return

    formatters = formatters or {}
    chip_columns = chip_columns or {}
    bar_columns = bar_columns or {}
    header_html = "".join(f"<th>{html.escape(str(column))}</th>" for column in dataframe.columns)
    rows_html: list[str] = []
    for _, row in dataframe.iterrows():
        cell_html: list[str] = []
        for column in dataframe.columns:
            value = row[column]
            if pd.isna(value):
                formatted_value = "-"
            elif column in formatters:
                formatted_value = format(value, formatters[column])
            else:
                formatted_value = str(value)
            escaped_value = html.escape(formatted_value)
            if column in chip_columns:
                chip_map = chip_columns[column]
                chip_class = chip_map.get(str(value), chip_map.get("__default__", "neutral"))
                escaped_value = f'<span class="table-chip {chip_class}">{escaped_value}</span>'
            elif column in bar_columns and isinstance(value, int | float):
                max_value = bar_columns[column]
                width_ratio = (
                    0.0 if max_value <= 0 else min(max(float(value) / max_value, 0.0), 1.0)
                )
                escaped_value = (
                    "<div>"
                    f"<div>{escaped_value}</div>"
                    '<div style="margin-top:0.35rem;height:0.36rem;'
                    "background:rgba(226,232,240,0.72);"
                    'border-radius:999px;overflow:hidden;">'
                    f'<div style="height:100%;width:{width_ratio * 100:.1f}%;'
                    'background:linear-gradient(90deg,#14b8a6,#1d4ed8);"></div>'
                    "</div></div>"
                )
            cell_html.append(f"<td>{escaped_value}</td>")
        rows_html.append(f"<tr>{''.join(cell_html)}</tr>")

    st.markdown(
        f"""
        <div class="table-card">
            <div class="table-scroll">
                <table class="table-grid">
                    <thead>
                        <tr>{header_html}</tr>
                    </thead>
                    <tbody>
                        {''.join(rows_html)}
                    </tbody>
                </table>
            </div>
        </div>
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
    st.markdown(
        f"""
        <div class="state-card">
            <strong>{title}</strong>
            <div>{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard_source_notice(
    labels: dict[str, str],
    *,
    demo_active: bool,
    demo_mode: str,
) -> None:
    if not demo_active:
        return
    st.markdown(
        f"""
        <div class="notice-card">
            <strong>{labels["demo_banner_title"]}</strong><br/>
            {labels["demo_banner_copy"].format(demo_mode=demo_mode)}
        </div>
        """,
        unsafe_allow_html=True,
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
