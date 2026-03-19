from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DEFAULT_THEME = {
    "bg": "#f3f6fb",
    "surface": "#ffffff",
    "surface_alt": "#f8fafc",
    "surface_dark": "#0f172a",
    "border": "#dbe4f0",
    "text": "#0f172a",
    "muted": "#5b6b82",
    "primary": "#0f5bd7",
    "primary_dark": "#0a3f97",
    "success": "#0f766e",
    "warning": "#b45309",
    "danger": "#b91c1c",
}


def apply_chart_style(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        font={"color": DEFAULT_THEME["text"], "family": "Segoe UI, Aptos, sans-serif", "size": 13},
        title_font={"color": DEFAULT_THEME["text"], "size": 18},
        plot_bgcolor=DEFAULT_THEME["surface"],
        paper_bgcolor=DEFAULT_THEME["surface"],
        margin={"l": 24, "r": 24, "t": 56, "b": 24},
        title_x=0.02,
    )
    fig.update_xaxes(gridcolor="#edf2f7")
    fig.update_yaxes(gridcolor="#edf2f7")
    return fig


def render_global_styles() -> None:
    st.markdown(
        f"""
        <style>
            .stApp {{
                background:
                    radial-gradient(circle at top right, rgba(15, 91, 215, 0.10), transparent 28%),
                    linear-gradient(180deg, {DEFAULT_THEME["bg"]} 0%, #eef3f9 100%);
                color: {DEFAULT_THEME["text"]};
            }}
            [data-testid="stHeader"] {{ background: transparent; }}
            [data-testid="stMainBlockContainer"] {{
                padding-top: 1.2rem;
                padding-bottom: 2.5rem;
                max-width: 1440px;
            }}
            [data-testid="stSidebar"] {{
                background: rgba(255, 255, 255, 0.92);
                border-right: 1px solid {DEFAULT_THEME["border"]};
            }}
            [data-testid="stSidebar"] > div:first-child {{
                padding-top: 1rem;
            }}
            .section-label {{
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 700;
                color: {DEFAULT_THEME["primary"]};
                margin-bottom: 0.3rem;
            }}
            .hero {{
                padding: 1.5rem 1.65rem;
                border-radius: 24px;
                background:
                    linear-gradient(135deg, rgba(10, 63, 151, 0.95), rgba(15, 91, 215, 0.90)),
                    linear-gradient(180deg, #0b1b35, #143259);
                color: #f8fbff;
                box-shadow: 0 24px 60px rgba(15, 23, 42, 0.14);
            }}
            .hero-grid {{
                display: grid;
                grid-template-columns: 1.9fr 1fr;
                gap: 1rem;
                align-items: end;
            }}
            .hero-badge {{
                display: inline-block;
                padding: 0.38rem 0.65rem;
                border-radius: 999px;
                background: rgba(255,255,255,0.12);
                font-size: 0.78rem;
                font-weight: 700;
                margin-bottom: 0.7rem;
            }}
            .hero h1 {{
                margin: 0;
                font-size: 2rem;
                line-height: 1.15;
                font-weight: 800;
                letter-spacing: -0.03em;
            }}
            .hero p {{
                margin: 0.55rem 0 0 0;
                color: rgba(248, 251, 255, 0.82);
                font-size: 0.98rem;
                max-width: 62ch;
            }}
            .hero-meta {{ display: flex; gap: 0.75rem; justify-content: flex-end; flex-wrap: wrap; }}
            .hero-stat {{
                min-width: 150px;
                padding: 0.9rem 1rem;
                border-radius: 16px;
                background: rgba(255, 255, 255, 0.12);
            }}
            .hero-stat-label {{
                font-size: 0.76rem;
                color: rgba(248, 251, 255, 0.72);
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 700;
            }}
            .hero-stat-value {{ font-size: 1.25rem; font-weight: 800; margin-top: 0.2rem; }}
            .panel {{
                background: rgba(255,255,255,0.88);
                border: 1px solid {DEFAULT_THEME["border"]};
                border-radius: 20px;
                padding: 1.15rem;
                box-shadow: 0 8px 30px rgba(15, 23, 42, 0.04);
            }}
            .panel-head {{
                display: flex;
                justify-content: space-between;
                gap: 1rem;
                align-items: flex-start;
                margin-bottom: 0.9rem;
            }}
            .panel-title {{
                color: {DEFAULT_THEME["text"]};
                font-size: 1.05rem;
                font-weight: 800;
                line-height: 1.2;
            }}
            .panel-caption {{
                color: {DEFAULT_THEME["muted"]};
                font-size: 0.88rem;
                margin-top: 0.15rem;
            }}
            .status-strip {{
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 0.85rem;
                margin: 1rem 0 1.25rem 0;
            }}
            .status-card {{
                background: rgba(255,255,255,0.88);
                border: 1px solid {DEFAULT_THEME["border"]};
                border-radius: 18px;
                padding: 0.95rem 1rem;
                box-shadow: 0 8px 30px rgba(15, 23, 42, 0.04);
            }}
            .status-label {{
                color: {DEFAULT_THEME["muted"]};
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-size: 0.72rem;
                font-weight: 800;
            }}
            .status-value {{
                color: {DEFAULT_THEME["text"]};
                font-size: 1.05rem;
                font-weight: 800;
                margin-top: 0.32rem;
            }}
            .status-sub {{
                color: {DEFAULT_THEME["muted"]};
                font-size: 0.82rem;
                margin-top: 0.25rem;
            }}
            .status-pill {{
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                padding: 0.36rem 0.62rem;
                border-radius: 999px;
                font-size: 0.76rem;
                font-weight: 800;
                border: 1px solid {DEFAULT_THEME["border"]};
                background: rgba(15, 91, 215, 0.08);
                color: {DEFAULT_THEME["primary_dark"]};
                white-space: nowrap;
            }}
            .status-pill.success {{
                background: rgba(15, 118, 110, 0.1);
                color: {DEFAULT_THEME["success"]};
                border-color: rgba(15, 118, 110, 0.18);
            }}
            .status-pill.warning {{
                background: rgba(180, 83, 9, 0.1);
                color: {DEFAULT_THEME["warning"]};
                border-color: rgba(180, 83, 9, 0.18);
            }}
            .status-pill.danger {{
                background: rgba(185, 28, 28, 0.1);
                color: {DEFAULT_THEME["danger"]};
                border-color: rgba(185, 28, 28, 0.18);
            }}
            .kpi-card {{
                background: linear-gradient(180deg, {DEFAULT_THEME["surface"]}, {DEFAULT_THEME["surface_alt"]});
                border: 1px solid {DEFAULT_THEME["border"]};
                border-radius: 18px;
                padding: 1rem;
                min-height: 126px;
                box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
            }}
            .kpi-title {{
                color: {DEFAULT_THEME["muted"]};
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 700;
            }}
            .kpi-value {{
                color: {DEFAULT_THEME["text"]};
                font-size: 1.85rem;
                font-weight: 800;
                margin-top: 0.45rem;
                line-height: 1.1;
            }}
            .kpi-sub {{ color: {DEFAULT_THEME["muted"]}; font-size: 0.86rem; margin-top: 0.35rem; }}
            .insight-list {{ margin: 0; padding-left: 1rem; color: {DEFAULT_THEME["text"]}; }}
            .insight-list li {{ margin-bottom: 0.55rem; line-height: 1.45; }}
            .empty-state {{
                padding: 2rem 1.5rem;
                text-align: center;
                border-radius: 20px;
                border: 1px dashed {DEFAULT_THEME["border"]};
                background: rgba(255,255,255,0.72);
            }}
            .footer {{
                margin-top: 1.25rem;
                padding: 1rem 1.15rem;
                border-radius: 18px;
                background: rgba(15, 23, 42, 0.96);
                color: #e2e8f0;
            }}
            .footer-title {{ font-weight: 800; margin-bottom: 0.2rem; }}
            .sidebar-block {{
                padding: 0.9rem 0.95rem;
                border: 1px solid {DEFAULT_THEME["border"]};
                border-radius: 16px;
                background: linear-gradient(180deg, #ffffff, #f8fbff);
                margin-bottom: 0.95rem;
            }}
            .sidebar-title {{
                font-size: 0.83rem;
                font-weight: 800;
                color: {DEFAULT_THEME["text"]};
                margin-bottom: 0.25rem;
            }}
            .sidebar-caption {{ font-size: 0.82rem; color: {DEFAULT_THEME["muted"]}; margin-bottom: 0.7rem; }}
            .sidebar-stat {{
                display: grid;
                gap: 0.15rem;
                padding: 0.7rem 0.75rem;
                border-radius: 14px;
                background: #f8fbff;
                border: 1px solid {DEFAULT_THEME["border"]};
                margin-top: 0.55rem;
            }}
            .sidebar-stat-label {{
                font-size: 0.72rem;
                font-weight: 800;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: {DEFAULT_THEME["muted"]};
            }}
            .sidebar-stat-value {{
                font-size: 0.95rem;
                font-weight: 800;
                color: {DEFAULT_THEME["text"]};
            }}
            [data-testid="stMetric"] {{
                background: linear-gradient(180deg, #ffffff, #f8fbff) !important;
                border: 1px solid {DEFAULT_THEME["border"]} !important;
                border-radius: 16px !important;
                padding: 0.8rem 0.95rem !important;
            }}
            [data-testid="stMetricLabel"] {{
                font-weight: 700 !important;
                color: {DEFAULT_THEME["muted"]} !important;
            }}
            [data-testid="stTabs"] [role="tablist"] {{ gap: 0.5rem; margin-bottom: 0.75rem; }}
            [data-testid="stTabs"] button[role="tab"] {{
                border-radius: 999px !important;
                padding: 0.55rem 0.95rem !important;
                border: 1px solid {DEFAULT_THEME["border"]} !important;
                background: rgba(255,255,255,0.9) !important;
                color: {DEFAULT_THEME["text"]} !important;
                font-weight: 700 !important;
            }}
            [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
                background: {DEFAULT_THEME["primary"]} !important;
                border-color: {DEFAULT_THEME["primary"]} !important;
            }}
            [data-testid="stTabs"] button[role="tab"][aria-selected="true"] p {{ color: #ffffff !important; }}
            .stButton > button, .stDownloadButton > button {{
                width: 100%;
                border-radius: 12px;
                border: 1px solid {DEFAULT_THEME["primary"]} !important;
                background: {DEFAULT_THEME["primary"]} !important;
                color: #ffffff !important;
                font-weight: 700 !important;
                min-height: 2.8rem;
            }}
            div[data-baseweb="select"] {{
                border-radius: 12px !important;
                border-color: {DEFAULT_THEME["border"]} !important;
            }}
            [data-testid="stExpander"] {{
                border: 1px solid {DEFAULT_THEME["border"]};
                border-radius: 18px;
                background: rgba(255,255,255,0.84);
            }}
            [data-testid="stDataFrame"] {{
                border: 1px solid {DEFAULT_THEME["border"]};
                border-radius: 18px;
                overflow: hidden;
            }}
            .block-spacer {{
                height: 0.45rem;
            }}
            @media (max-width: 980px) {{
                .hero-grid {{ grid-template-columns: 1fr; }}
                .hero-meta {{ justify-content: flex-start; }}
                .status-strip {{ grid-template-columns: 1fr 1fr; }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(eyebrow: str, title: str, caption: str) -> None:
    st.markdown(
        f"""
        <div style="margin: 0.25rem 0 0.85rem 0;">
            <div class="section-label">{eyebrow}</div>
            <div style="font-size:1.42rem;font-weight:800;color:{DEFAULT_THEME["text"]};">{title}</div>
            <div style="color:{DEFAULT_THEME["muted"]};margin-top:0.15rem;">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(title: str, value: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_panel_header(eyebrow: str, title: str, caption: str, pill: str | None = None) -> None:
    pill_markup = f'<div class="status-pill">{pill}</div>' if pill else ""
    st.markdown(
        f"""
        <div class="panel-head">
            <div>
                <div class="section-label">{eyebrow}</div>
                <div class="panel-title">{title}</div>
                <div class="panel-caption">{caption}</div>
            </div>
            {pill_markup}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_strip(items: list[dict[str, str]]) -> None:
    cards = []
    for item in items:
        cards.append(
            f"""
            <div class="status-card">
                <div class="status-label">{item["label"]}</div>
                <div class="status-value">{item["value"]}</div>
                <div class="status-sub">{item["subtitle"]}</div>
            </div>
            """
        )
    st.markdown(f'<div class="status-strip">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_status_pill(label: str, value: str, tone: str = "neutral") -> None:
    tone_class = tone if tone in {"success", "warning", "danger"} else ""
    st.markdown(
        f'<div class="status-pill {tone_class}">{label}: {value}</div>',
        unsafe_allow_html=True,
    )


def render_chart_panel(
    *,
    eyebrow: str,
    title: str,
    caption: str,
    fig: go.Figure,
) -> None:
    render_panel_header(eyebrow, title, caption)
    st.plotly_chart(apply_chart_style(fig), use_container_width=True, theme=None)


def render_dataframe_panel(
    *,
    eyebrow: str,
    title: str,
    caption: str,
    frame: pd.DataFrame | pd.io.formats.style.Styler,
    height: int | None = None,
) -> None:
    render_panel_header(eyebrow, title, caption)
    st.dataframe(frame, use_container_width=True, hide_index=True, height=height)


def render_empty_state(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="empty-state">
            <div style="font-size:1.15rem;font-weight:800;color:{DEFAULT_THEME["text"]};">
                {title}
            </div>
            <div style="margin-top:0.4rem;color:{DEFAULT_THEME["muted"]};">
                {body}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer(title: str, body: str, timestamp_label: str) -> None:
    st.markdown(
        f"""
        <div class="footer">
            <div class="footer-title">{title}</div>
            <div>{body}</div>
            <div style="margin-top:0.45rem;color:#94a3b8;">{timestamp_label.format(dt=datetime.now().strftime("%d/%m/%Y %H:%M"))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
